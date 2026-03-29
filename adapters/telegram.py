import httpx
from typing import Optional, List, Dict, Any
from models.telegram import TelegramMessage


class TelegramClient:
    """Клиент для работы с Telegram Bot API"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Отправка сообщения через Telegram Bot API
        
        Args:
            chat_id: ID чата или username канала
            text: Текст сообщения
            parse_mode: Режим парсинга (Markdown, HTML)
            reply_to_message_id: ID сообщения для ответа
            **kwargs: Дополнительные параметры API
        
        Returns:
            Ответ от Telegram API
        """
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        payload.update(kwargs)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30,
        allowed_updates: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Получение обновлений через long polling
        
        Returns:
            Список обновлений
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "timeout": timeout,
        }
        
        if offset is not None:
            params["offset"] = offset
        if allowed_updates:
            params["allowed_updates"] = allowed_updates
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getUpdates",
                params=params,
                timeout=timeout + 5
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", [])
    
    async def set_webhook(
        self,
        url: str,
        certificate: Optional[str] = None,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Установка webhook для получения обновлений
        
        Args:
            url: HTTPS URL для получения webhook
            certificate: Публичный ключ сертификата (опционально)
            max_connections: Максимальное количество соединений
            allowed_updates: Список типов обновлений
        
        Returns:
            Ответ от Telegram API
        """
        payload: Dict[str, Any] = {
            "url": url,
            "max_connections": max_connections,
        }
        
        if certificate:
            payload["certificate"] = certificate
        if allowed_updates:
            payload["allowed_updates"] = allowed_updates
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/setWebhook",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def delete_webhook(self) -> Dict[str, Any]:
        """Удаление webhook"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/deleteWebhook",
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    async def get_me(self) -> Dict[str, Any]:
        """Получение информации о боте"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/getMe",
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
    
    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: bool = False
    ) -> Dict[str, Any]:
        """Ответ на callback query"""
        payload: Dict[str, Any] = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
        }
        
        if text:
            payload["text"] = text
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/answerCallbackQuery",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
