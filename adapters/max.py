import httpx
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
from models.max import MaxMessage, MaxResponse, MaxIncomingMessage, MaxUser, MaxChat
from utils.logger import setup_logger
from utils.constants import (
    DEFAULT_HTTP_TIMEOUT,
    LONG_POLLING_TIMEOUT,
    HEALTH_CHECK_TIMEOUT,
    POLLING_ERROR_DELAY
)


class MaxClient:
    """
    Клиент для работы с MAX Messenger API
    
    На основе документации: https://dev.max.ru/docs/chatbots/bots-coding/hellobot/go
    
    MAX API использует:
    - Токен бота для аутентификации
    - Long polling или WebSocket для получения обновлений
    - HTTP POST для отправки сообщений
    
    Примечание: Официальный SDK доступен на Go. Данный клиент реализует
    предполагаемый HTTP API на основе примеров использования SDK.
    """
    
    # Предположительный базовый URL (уточните в документации MAX)
    DEFAULT_BASE_URL = "https://api.max.ru/bot"
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_token: str = "",
        send_endpoint: str = "/messages/send",
        receive_endpoint: str = "/updates/get",
        timeout: int = 30
    ):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_token = api_token
        self.send_endpoint = send_endpoint
        self.receive_endpoint = receive_endpoint
        self.timeout = timeout
        self.logger = setup_logger(__name__)
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Получение заголовков для запросов
        
        MAX API использует токен бота для аутентификации.
        Токен может передаваться:
        - В заголовке Authorization: Bearer <token>
        - В заголовке X-Bot-Token: <token>
        - В параметре URL
        """
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
    
    def _get_url(self, endpoint: str) -> str:
        """Получение полного URL endpoint'а"""
        # Если токен передаётся в URL (как в Telegram API)
        return f"{self.base_url}/{self.api_token}{endpoint}"
    
    async def send_message(self, message: MaxMessage) -> MaxResponse:
        """
        Отправка сообщения через MAX API
        
        На основе Go SDK: api.Messages.Send(...)
        
        Args:
            message: Объект сообщения для отправки
        
        Returns:
            Ответ от MAX API
        """
        payload = {
            "chat_id": message.chat_id,
            "text": message.text,
        }
        
        if message.reply_to_message_id:
            payload["reply_to_message_id"] = message.reply_to_message_id
        if message.parse_mode:
            payload["parse_mode"] = message.parse_mode
        if message.extra:
            payload.update(message.extra)
        
        try:
            client = self._get_client()
            response = await client.post(
                self._get_url(self.send_endpoint),
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            self.logger.debug(f"Message sent to MAX chat {message.chat_id}")
            
            return MaxResponse(
                success=data.get("ok", data.get("success", True)),
                message_id=str(data.get("message_id", "")),
                chat_id=data.get("chat_id"),
                timestamp=data.get("date"),
                error=data.get("description") or data.get("error"),
                data=data
            )
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send message to MAX: {e}")
            raise
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30
    ) -> List[MaxIncomingMessage]:
        """
        Получение входящих сообщений от MAX API (long polling)
        
        На основе Go SDK: api.GetUpdates(ctx)
        
        Args:
            offset: ID последнего полученного сообщения
            limit: Максимальное количество сообщений
            timeout: Таймаут long polling
        
        Returns:
            Список входящих сообщений
        """
        params = {
            "limit": limit,
            "timeout": timeout,
        }
        if offset is not None:
            params["offset"] = offset
        
        try:
            client = self._get_client()
            response = await client.get(
                self._get_url(self.receive_endpoint),
                params=params,
                headers=self._get_headers(),
                timeout=timeout + 10
            )
            response.raise_for_status()
            data = response.json()
            
            messages = []
            for msg_data in data.get("result", data.get("updates", [])):
                # Парсинг сообщения в формате MAX
                # Адаптируйте под реальный формат ответа MAX API
                update_obj = msg_data.get("message", msg_data)
                
                from_user = None
                if update_obj.get("from"):
                    from_user = MaxUser(**update_obj["from"])
                
                chat = MaxChat(
                    id=str(update_obj.get("chat", {}).get("id", "unknown")),
                    type=update_obj.get("chat", {}).get("type", "private"),
                    name=update_obj.get("chat", {}).get("title")
                )
                
                messages.append(MaxIncomingMessage(
                    message_id=str(update_obj.get("message_id", "")),
                    from_user=from_user,
                    chat=chat,
                    timestamp=update_obj.get("date", 0),
                    text=update_obj.get("text"),
                    type=update_obj.get("type", "text"),
                ))
            
            self.logger.debug(f"Received {len(messages)} updates from MAX")
            return messages
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get updates from MAX: {e}")
            raise
    
    async def get_updates_stream(
        self,
        offset: Optional[int] = None
    ) -> AsyncGenerator[MaxIncomingMessage, None]:
        """
        Постоянный поток обновлений от MAX API
        
        Генератор для непрерывного получения сообщений
        """
        current_offset = offset
        
        while True:
            try:
                updates = await self.get_updates(offset=current_offset, timeout=LONG_POLLING_TIMEOUT)
                
                for update in updates:
                    yield update
                    current_offset = int(update.message_id) + 1 if update.message_id.isdigit() else current_offset
                
                if not updates:
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Error getting updates: {e}")
                await asyncio.sleep(POLLING_ERROR_DELAY)
    
    async def set_webhook(
        self,
        url: str,
        secret_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Установка webhook для получения обновлений
        
        Args:
            url: HTTPS URL для webhook
            secret_token: Секретный токен для проверки запросов
        
        Returns:
            Ответ от MAX API
        """
        payload = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token
        
        try:
            client = self._get_client()
            response = await client.post(
                self._get_url("/webhook/set"),
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            self.logger.info(f"MAX webhook set to {url}")
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to set MAX webhook: {e}")
            raise
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Удаление webhook"""
        try:
            client = self._get_client()
            response = await client.post(
                self._get_url("/webhook/delete"),
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            self.logger.info("MAX webhook deleted")
            return response.json()
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to delete MAX webhook: {e}")
            raise
    
    async def get_me(self) -> Dict[str, Any]:
        """
        Получение информации о боте
        
        Returns:
            Информация о боте MAX
        """
        try:
            client = self._get_client()
            response = await client.get(
                self._get_url("/me"),
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            bot_info = result.get("result", {})
            self.logger.debug("MAX bot info retrieved")
            return bot_info
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get MAX bot info: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка доступности MAX API"""
        try:
            client = self._get_client()
            response = await client.get(
                self._get_url("/me"),
                headers=self._get_headers(),
                timeout=HEALTH_CHECK_TIMEOUT
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"MAX API health check failed: {e}")
            return False
