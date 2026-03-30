from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
import asyncio
import logging

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse

from config import settings
from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from services.proxy import ProxyService
from models.telegram import TelegramUpdate
from models.max import MaxIncomingMessage
from utils.logger import setup_logger
from utils.constants import (
    STATUS_RUNNING,
    STATUS_HEALTHY,
    STATUS_DEGRADED,
    STATUS_CONNECTED,
    STATUS_DISCONNECTED,
    MSG_SERVICE_NOT_INITIALIZED,
    MSG_CLIENT_NOT_INITIALIZED,
    LONG_POLLING_TIMEOUT,
    POLLING_ERROR_DELAY
)


# Setup logger
logger = setup_logger(__name__, settings.log_level)

# Глобальные клиенты
telegram_client: TelegramClient | None = None
max_client: MaxClient | None = None
proxy_service: ProxyService | None = None
polling_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Инициализация и очистка ресурсов приложения"""
    global telegram_client, max_client, proxy_service, polling_task

    logger.info("Starting Telegram → MAX Messenger Proxy")

    # Инициализация клиентов
    telegram_client = TelegramClient(bot_token=settings.telegram_bot_token)
    max_client = MaxClient(
        base_url=settings.max_api_base_url,
        api_token=settings.max_api_token,
        send_endpoint=settings.max_send_endpoint,
        receive_endpoint=settings.max_receive_endpoint,
        timeout=settings.max_timeout
    )
    proxy_service = ProxyService(
        telegram_client=telegram_client,
        max_client=max_client,
        chat_user_mapping=settings.chat_user_mapping
    )

    # Проверка подключения к Telegram
    try:
        bot_info = await telegram_client.get_me()
        logger.info(f"✓ Telegram bot connected: @{bot_info.get('username', 'unknown')}")
    except Exception as e:
        logger.error(f"⚠ Failed to connect to Telegram: {e}")

    # Проверка подключения к MAX API
    try:
        if await max_client.health_check():
            logger.info("✓ MAX API is available")
        else:
            logger.warning("⚠ MAX API is not available")
    except Exception as e:
        logger.error(f"⚠ Failed to connect to MAX API: {e}")

    # Запуск polling режима если указано в конфиге
    if settings.max_mode == "polling" and max_client and proxy_service:
        polling_task = asyncio.create_task(max_polling_loop())
        logger.info("✓ MAX polling mode started")

    yield

    # Остановка polling задачи
    if polling_task:
        logger.info("Stopping polling task...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            logger.info("Polling task stopped")

    # Закрытие HTTP клиентов
    if telegram_client:
        await telegram_client.close()
    if max_client:
        await max_client.close()

    # Очистка
    telegram_client = None
    max_client = None
    proxy_service = None
    
    logger.info("Proxy service stopped")


async def max_polling_loop():
    """
    Фоновый цикл для опроса MAX API (long polling)
    
    Получает сообщения из MAX и пересылает их в Telegram
    """
    if not max_client or not proxy_service or not telegram_client:
        logger.error("Cannot start polling: clients not initialized")
        return
    
    offset = None
    logger.info("Starting MAX API polling loop...")
    
    while True:
        try:
            updates = await max_client.get_updates(offset=offset, timeout=LONG_POLLING_TIMEOUT)
            
            for update in updates:
                # Пересылка сообщения из MAX в Telegram
                await forward_max_to_telegram(update, telegram_client, proxy_service)
                
                # Обновление offset для следующего запроса
                if update.message_id and update.message_id.isdigit():
                    offset = int(update.message_id) + 1
            
        except asyncio.CancelledError:
            logger.info("Polling loop cancelled")
            break
        except Exception as e:
            logger.error(f"Polling error: {e}")
            await asyncio.sleep(POLLING_ERROR_DELAY)


async def forward_max_to_telegram(
    message: MaxIncomingMessage,
    tg_client: TelegramClient,
    proxy: ProxyService
):
    """
    Пересылка сообщения из MAX в Telegram
    """
    # Получение Telegram chat_id из маппинга или использование chat.id
    tg_chat_id = None
    
    if proxy.chat_user_mapping:
        # Поиск Telegram chat_id по MAX user_id
        for tg_id, max_id in proxy.chat_user_mapping.items():
            if max_id == message.chat.id:
                tg_chat_id = int(tg_id)
                break
    
    if tg_chat_id is None:
        # Если маппинга нет, используем chat.id как fallback
        # (это может не работать, если ID форматы не совпадают)
        try:
            tg_chat_id = int(message.chat.id)
        except ValueError:
            logger.warning(f"Cannot convert chat_id: {message.chat.id}")
            return
    
    # Отправка в Telegram
    try:
        await tg_client.send_message(
            chat_id=tg_chat_id,
            text=message.text or "",
        )
        logger.info(f"Message forwarded from MAX chat {message.chat.id} to Telegram chat {tg_chat_id}")
    except Exception as e:
        logger.error(f"Failed to send to Telegram: {e}")


app = FastAPI(
    title="Telegram → MAX Messenger Proxy",
    description="Прокси-сервис для передачи сообщений между Telegram Bot API и MAX Messenger API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Информация о сервисе"""
    return {
        "service": "Telegram → MAX Messenger Proxy",
        "version": "1.0.0",
        "status": STATUS_RUNNING
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Проверка здоровья сервиса"""
    telegram_ok = False
    max_ok = False
    
    if telegram_client:
        try:
            await telegram_client.get_me()
            telegram_ok = True
        except Exception as e:
            logger.warning(f"Telegram health check failed: {e}")
    
    if max_client:
        try:
            max_ok = await max_client.health_check()
        except Exception as e:
            logger.warning(f"MAX health check failed: {e}")
    
    status = STATUS_HEALTHY if telegram_ok and max_ok else STATUS_DEGRADED
    
    return {
        "status": status,
        "telegram_api": STATUS_CONNECTED if telegram_ok else STATUS_DISCONNECTED,
        "max_api": STATUS_CONNECTED if max_ok else STATUS_DISCONNECTED
    }


@app.post(settings.telegram_webhook_path)
async def telegram_webhook(update: TelegramUpdate) -> JSONResponse:
    """
    Webhook endpoint для получения обновлений от Telegram
    
    Telegram отправляет POST запросы с обновлениями на этот endpoint
    """
    if not proxy_service:
        logger.error("Webhook called but service not initialized")
        raise HTTPException(status_code=503, detail=MSG_SERVICE_NOT_INITIALIZED)
    
    try:
        # Обработка сообщения
        response = await proxy_service.process_telegram_message(update)
        
        if response:
            return JSONResponse({
                "status": "processed",
                "max_response": {
                    "success": response.success,
                    "message_id": response.message_id
                }
            })
        
        return JSONResponse({"status": "ignored"})
    
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        
        # Попытка уведомления об ошибке
        if update.message and proxy_service.telegram_client:
            try:
                await proxy_service.telegram_client.send_message(
                    chat_id=update.message.chat.id,
                    text=f"⚠ Ошибка обработки: {str(e)}"
                )
            except Exception as notify_error:
                logger.error(f"Failed to send error notification: {notify_error}")
        
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/telegram/send")
async def send_telegram_message(
    chat_id: int,
    text: str,
    reply_to_message_id: int | None = None
) -> Dict[str, Any]:
    """
    Отправка сообщения в Telegram через API сервиса
    
    Полезно для отправки уведомлений из MAX в Telegram
    """
    if not proxy_service:
        logger.error("Send message called but service not initialized")
        raise HTTPException(status_code=503, detail=MSG_SERVICE_NOT_INITIALIZED)
    
    try:
        result = await proxy_service.forward_to_telegram(
            text=text,
            tg_chat_id=chat_id,
            reply_to_message_id=reply_to_message_id
        )
        logger.info(f"Message sent to Telegram chat {chat_id}")
        return {"status": "sent", "result": result}
    
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/set")
async def set_webhook(webhook_url: str) -> Dict[str, Any]:
    """
    Установка webhook в Telegram Bot API
    
    Вызовите этот endpoint для регистрации webhook в Telegram
    """
    if not telegram_client:
        logger.error("Set webhook called but Telegram client not initialized")
        raise HTTPException(status_code=503, detail=MSG_CLIENT_NOT_INITIALIZED)
    
    try:
        result = await telegram_client.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        return {"status": "ok", "result": result}
    
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/delete")
async def delete_webhook() -> Dict[str, Any]:
    """Удаление webhook из Telegram Bot API"""
    if not telegram_client:
        logger.error("Delete webhook called but Telegram client not initialized")
        raise HTTPException(status_code=503, detail=MSG_CLIENT_NOT_INITIALIZED)
    
    try:
        result = await telegram_client.delete_webhook()
        logger.info("Webhook deleted")
        return {"status": "ok", "result": result}
    
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bot/info")
async def get_bot_info() -> Dict[str, Any]:
    """Получение информации о Telegram боте"""
    if not telegram_client:
        logger.error("Get bot info called but Telegram client not initialized")
        raise HTTPException(status_code=503, detail=MSG_CLIENT_NOT_INITIALIZED)
    
    try:
        bot_info = await telegram_client.get_me()
        return {"status": "ok", "result": bot_info}
    
    except Exception as e:
        logger.error(f"Failed to get bot info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=True
    )
