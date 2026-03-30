from typing import Optional, Dict, Any
from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from models.telegram import TelegramMessage, TelegramUpdate
from models.max import MaxMessage, MaxResponse
from config import settings
from utils.logger import setup_logger


class ProxyService:
    """
    Сервис для проксирования сообщений между Telegram и MAX Messenger
    
    Выполняет маппинг форматов сообщений и маршрутизацию
    """
    
    def __init__(
        self,
        telegram_client: TelegramClient,
        max_client: MaxClient,
        chat_user_mapping: Optional[Dict[str, str]] = None
    ):
        self.telegram_client = telegram_client
        self.max_client = max_client
        self.chat_user_mapping = chat_user_mapping or {}
        self.logger = setup_logger(__name__)
    
    def telegram_to_max(self, tg_message: TelegramMessage) -> MaxMessage:
        """
        Конвертация сообщения Telegram в формат MAX
        
        Args:
            tg_message: Сообщение из Telegram
        
        Returns:
            Сообщение в формате MAX
        """
        # Определение chat_id для MAX
        # Приоритеты:
        # 1. Явный маппинг из конфига
        # 2. ID чата Telegram как строка
        # 3. ID пользователя если это личный чат
        
        chat_id = str(tg_message.chat.id)
        
        # Проверка маппинга
        if self.chat_user_mapping:
            chat_id = self.chat_user_mapping.get(
                str(tg_message.chat.id),
                chat_id
            )
        
        # Извлечение текста сообщения
        text = tg_message.text or ""
        
        # Если есть reply, добавляем информацию
        if tg_message.reply_to_message:
            text = f"Re: {text}"
        
        return MaxMessage(
            chat_id=chat_id,
            text=text,
            reply_to_message_id=(
                str(tg_message.reply_to_message.message_id)
                if tg_message.reply_to_message else None
            ),
        )
    
    def max_to_telegram(self, max_response: MaxResponse, tg_chat_id: int) -> Dict[str, Any]:
        """
        Конвертация ответа MAX в формат для отправки в Telegram
        
        Args:
            max_response: Ответ от MAX API
            tg_chat_id: ID чата Telegram для ответа
        
        Returns:
            Параметры для отправки в Telegram
        """
        if max_response.error:
            return {
                "chat_id": tg_chat_id,
                "text": f"❌ Ошибка: {max_response.error}"
            }
        
        return {
            "chat_id": tg_chat_id,
            "text": "✅ Сообщение отправлено",
        }
    
    async def process_telegram_message(
        self,
        update: TelegramUpdate
    ) -> Optional[MaxResponse]:
        """
        Обработка входящего сообщения из Telegram и отправка в MAX
        
        Args:
            update: Обновление из Telegram
        
        Returns:
            Ответ от MAX API или None
        """
        # Извлечение сообщения из update
        message = (
            update.message or
            update.edited_message or
            update.channel_post or
            update.edited_channel_post
        )
        
        if not message:
            self.logger.debug("No message in update, skipping")
            return None
        
        # Игнорирование сообщений от ботов (опционально)
        if message.from_user and message.from_user.is_bot:
            self.logger.debug(f"Ignoring bot message from {message.from_user.id}")
            return None
        
        # Конвертация в формат MAX
        max_message = self.telegram_to_max(message)
        
        # Отправка в MAX
        try:
            response = await self.max_client.send_message(max_message)
            self.logger.info(f"Message forwarded from Telegram chat {message.chat.id} to MAX chat {max_message.chat_id}")
            return response
        except Exception as e:
            # Логирование ошибки
            self.logger.error(f"Error sending to MAX: {e}")
            
            # Уведомление об ошибке в Telegram
            try:
                await self.telegram_client.send_message(
                    chat_id=message.chat.id,
                    text=f"❌ Ошибка отправки в MAX: {str(e)}"
                )
            except Exception as notify_error:
                self.logger.error(f"Failed to send error notification: {notify_error}")
            return None
    
    async def forward_to_telegram(
        self,
        text: str,
        tg_chat_id: int,
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Прямая отправка сообщения в Telegram
        
        Args:
            text: Текст сообщения
            tg_chat_id: ID чата Telegram
            reply_to_message_id: ID сообщения для ответа
        
        Returns:
            Ответ от Telegram API
        """
        return await self.telegram_client.send_message(
            chat_id=tg_chat_id,
            text=text,
            reply_to_message_id=reply_to_message_id
        )
    
    async def sync_messages(
        self,
        tg_chat_id: int,
        max_chat_id: str
    ) -> None:
        """
        Синхронизация сообщений между чатами
        
        TODO: Реализуйте логику синхронизации при необходимости
        """
        pass
