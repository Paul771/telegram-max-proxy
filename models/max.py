from pydantic import BaseModel
from typing import Optional, List, Any


class MaxUser(BaseModel):
    """Пользователь MAX Messenger"""
    id: str
    username: Optional[str] = None
    display_name: Optional[str] = None


class MaxChat(BaseModel):
    """Чат в MAX Messenger"""
    id: str
    type: str = "private"  # private, group, channel
    name: Optional[str] = None


class MaxMessage(BaseModel):
    """Сообщение для отправки в MAX API"""
    chat_id: str
    text: str
    reply_to_message_id: Optional[str] = None
    parse_mode: Optional[str] = None  # markdown, html
    entities: Optional[List[Any]] = None
    
    # Дополнительные поля могут быть добавлены в зависимости от MAX API
    extra: Optional[dict] = None


class MaxResponse(BaseModel):
    """Ответ от MAX API"""
    success: bool
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    timestamp: Optional[int] = None
    error: Optional[str] = None
    data: Optional[dict] = None


class MaxIncomingMessage(BaseModel):
    """Входящее сообщение от MAX API (для webhook/long polling)"""
    message_id: str
    from_user: Optional[MaxUser] = None
    chat: MaxChat
    timestamp: int
    text: Optional[str] = None
    type: str = "text"  # text, image, video, etc.
    attachments: Optional[List[Any]] = None
