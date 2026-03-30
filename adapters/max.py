import httpx
import asyncio
from typing import Optional, List, Dict, Any
from models.max import (
    MaxNewMessageBody,
    MaxSendMessageResponse,
    MaxUpdate,
    MaxUpdatesResponse,
    MaxUser,
    TextFormat,
    InlineKeyboardButton
)
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
    
    Документация: https://dev.max.ru/docs-api
    
    MAX API использует:
    - Токен бота для аутентификации через заголовок Authorization
    - Long polling или Webhook для получения обновлений
    - HTTP методы для работы с сообщениями
    
    Базовый URL: https://platform-api.max.ru
    """
    
    DEFAULT_BASE_URL = "https://platform-api.max.ru"
    
    def __init__(
        self,
        api_token: str,
        base_url: Optional[str] = None,
        timeout: int = 30
    ):
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_token = api_token
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
        
        MAX API требует токен в заголовке Authorization
        """
        return {
            "Authorization": self.api_token,
            "Content-Type": "application/json",
        }
    
    async def get_me(self) -> MaxUser:
        """
        Получение информации о боте
        
        GET /me
        
        Returns:
            Информация о боте
        """
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.base_url}/me",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            self.logger.debug(f"Bot info retrieved: {data.get('name', 'unknown')}")
            return MaxUser(**data)
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get bot info: {e}")
            raise
    
    async def send_message(
        self,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
        text: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
        link: Optional[dict] = None,
        notify: bool = True,
        format: Optional[TextFormat] = None,
        disable_link_preview: bool = False
    ) -> MaxSendMessageResponse:
        """
        Отправка сообщения через MAX API
        
        POST /messages
        
        Args:
            user_id: ID пользователя для отправки в личку
            chat_id: ID чата для отправки в групповой чат
            text: Текст сообщения (до 4000 символов)
            attachments: Вложения (например, inline клавиатура)
            link: Ссылка на сообщение (reply/forward)
            notify: Уведомлять ли участников
            format: Формат текста (markdown или html)
            disable_link_preview: Отключить превью ссылок
        
        Returns:
            Ответ от MAX API с отправленным сообщением
        """
        if not user_id and not chat_id:
            raise ValueError("Either user_id or chat_id must be provided")
        
        # Формирование query параметров
        params = {}
        if user_id:
            params["user_id"] = user_id
        if chat_id:
            params["chat_id"] = chat_id
        if disable_link_preview:
            params["disable_link_preview"] = "true"
        
        # Формирование тела запроса
        body = MaxNewMessageBody(
            text=text,
            attachments=attachments,
            link=link,
            notify=notify,
            format=format
        )
        
        # Удаляем None значения
        payload = body.model_dump(exclude_none=True)
        
        try:
            client = self._get_client()
            response = await client.post(
                f"{self.base_url}/messages",
                params=params,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            self.logger.debug(f"Message sent to MAX (user_id={user_id}, chat_id={chat_id})")
            
            return MaxSendMessageResponse(**data)
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to send message to MAX: {e}")
            raise
    
    async def get_updates(
        self,
        limit: int = 100,
        timeout: int = 30,
        marker: Optional[int] = None,
        types: Optional[List[str]] = None
    ) -> MaxUpdatesResponse:
        """
        Получение обновлений от MAX API (long polling)
        
        GET /updates
        
        Args:
            limit: Максимальное количество обновлений (1-1000)
            timeout: Таймаут long polling (0-90 секунд)
            marker: Маркер последнего полученного обновления
            types: Список типов обновлений для фильтрации
        
        Returns:
            Список обновлений и маркер для следующего запроса
        """
        params: Dict[str, Any] = {
            "limit": min(max(limit, 1), 1000),
            "timeout": min(max(timeout, 0), 90),
        }
        
        if marker is not None:
            params["marker"] = marker
        
        if types:
            params["types"] = ",".join(types)
        
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.base_url}/updates",
                params=params,
                headers=self._get_headers(),
                timeout=timeout + 10
            )
            response.raise_for_status()
            data = response.json()
            
            updates_response = MaxUpdatesResponse(**data)
            self.logger.debug(f"Received {len(updates_response.updates)} updates from MAX")
            
            return updates_response
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to get updates from MAX: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Проверка доступности MAX API"""
        try:
            client = self._get_client()
            response = await client.get(
                f"{self.base_url}/me",
                headers=self._get_headers(),
                timeout=HEALTH_CHECK_TIMEOUT
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"MAX API health check failed: {e}")
            return False
