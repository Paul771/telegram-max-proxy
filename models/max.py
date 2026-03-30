from pydantic import BaseModel, Field
from typing import Optional, List, Any, Literal
from enum import Enum


class TextFormat(str, Enum):
    """Форматы текста в MAX"""
    MARKDOWN = "markdown"
    HTML = "html"


class ButtonType(str, Enum):
    """Типы кнопок inline клавиатуры"""
    CALLBACK = "callback"
    LINK = "link"
    REQUEST_CONTACT = "request_contact"
    REQUEST_GEO_LOCATION = "request_geo_location"
    OPEN_APP = "open_app"
    MESSAGE = "message"


class MaxUser(BaseModel):
    """Пользователь MAX Messenger согласно API"""
    user_id: int = Field(..., description="ID пользователя")
    name: str = Field(..., description="Имя пользователя")
    username: Optional[str] = Field(None, description="Username пользователя")
    is_bot: bool = Field(default=False, description="Является ли пользователь ботом")
    last_activity_time: Optional[int] = Field(None, description="Время последней активности")


class MaxChat(BaseModel):
    """Чат в MAX Messenger"""
    chat_id: int = Field(..., description="ID чата")
    type: Literal["dialog", "chat", "channel"] = Field(..., description="Тип чата")
    title: Optional[str] = Field(None, description="Название чата")
    description: Optional[str] = Field(None, description="Описание чата")


class MaxRecipient(BaseModel):
    """Получатель сообщения в MAX"""
    chat_id: Optional[int] = Field(None, description="ID чата")
    user_id: Optional[int] = Field(None, description="ID пользователя")
    chat_type: Optional[str] = Field(None, description="Тип чата")


class InlineKeyboardButton(BaseModel):
    """Кнопка inline клавиатуры"""
    type: ButtonType = Field(..., description="Тип кнопки")
    text: str = Field(..., max_length=128, description="Текст на кнопке")
    payload: Optional[str] = Field(None, description="Данные для callback кнопки")
    url: Optional[str] = Field(None, max_length=2048, description="URL для link кнопки")


class InlineKeyboardAttachment(BaseModel):
    """Вложение с inline клавиатурой"""
    type: Literal["inline_keyboard"] = "inline_keyboard"
    payload: dict = Field(..., description="Payload с кнопками")


class MaxMessageLink(BaseModel):
    """Ссылка на сообщение (reply/forward)"""
    type: Literal["reply", "forward"] = Field(..., description="Тип ссылки")
    message: Optional[dict] = Field(None, description="Связанное сообщение")


class MaxNewMessageBody(BaseModel):
    """Тело нового сообщения для отправки в MAX API"""
    text: Optional[str] = Field(None, max_length=4000, description="Текст сообщения")
    attachments: Optional[List[dict]] = Field(None, description="Вложения сообщения")
    link: Optional[MaxMessageLink] = Field(None, description="Ссылка на сообщение")
    notify: bool = Field(default=True, description="Уведомлять ли участников")
    format: Optional[TextFormat] = Field(None, description="Формат текста")


class MaxMessageBody(BaseModel):
    """Тело сообщения от MAX API"""
    text: Optional[str] = Field(None, description="Текст сообщения")
    attachments: Optional[List[dict]] = Field(None, description="Вложения")


class MaxMessage(BaseModel):
    """Сообщение в MAX согласно API"""
    sender: Optional[MaxUser] = Field(None, description="Отправитель")
    recipient: MaxRecipient = Field(..., description="Получатель")
    timestamp: int = Field(..., description="Unix timestamp")
    link: Optional[dict] = Field(None, description="Связанное сообщение")
    body: Optional[MaxMessageBody] = Field(None, description="Тело сообщения")
    stat: Optional[dict] = Field(None, description="Статистика (для каналов)")
    url: Optional[str] = Field(None, description="Публичная ссылка")


class MaxUpdate(BaseModel):
    """Обновление от MAX API"""
    update_type: str = Field(..., description="Тип обновления")
    timestamp: int = Field(..., description="Unix timestamp события")
    message: Optional[MaxMessage] = Field(None, description="Сообщение")
    user_locale: Optional[str] = Field(None, description="Язык пользователя")


class MaxUpdatesResponse(BaseModel):
    """Ответ на запрос обновлений"""
    updates: List[MaxUpdate] = Field(default_factory=list, description="Список обновлений")
    marker: Optional[int] = Field(None, description="Маркер для следующей страницы")


class MaxSendMessageResponse(BaseModel):
    """Ответ на отправку сообщения"""
    message: MaxMessage = Field(..., description="Отправленное сообщение")
