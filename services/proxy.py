from typing import Optional, Dict, Any, List
from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from models.telegram import TelegramMessage, TelegramUpdate
from models.max import MaxSendMessageResponse, TextFormat, InlineKeyboardButton
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
    
    def _convert_telegram_keyboard_to_max(self, reply_markup: dict) -> Optional[List[dict]]:
        """
        Конвертация Telegram inline клавиатуры в формат MAX
        
        Args:
            reply_markup: Telegram reply_markup
        
        Returns:
            Attachments для MAX API
        """
        if not reply_markup or "inline_keyboard" not in reply_markup:
            return None
        
        inline_keyboard = reply_markup["inline_keyboard"]
        max_buttons = []
        
        for row in inline_keyboard:
            max_row = []
            for button in row:
                max_button = {
                    "text": button.get("text", ""),
                }
                
                # Маппинг типов кнопок
                if "url" in button:
                    max_button["type"] = "link"
                    max_button["url"] = button["url"]
                elif "callback_data" in button:
                    max_button["type"] = "callback"
                    max_button["payload"] = button["callback_data"]
                else:
                    # По умолчанию callback
                    max_button["type"] = "callback"
                    max_button["payload"] = button.get("text", "")
                
                max_row.append(max_button)
            
            if max_row:
                max_buttons.append(max_row)
        
        if not max_buttons:
            return None
        
        return [{
            "type": "inline_keyboard",
            "payload": {
                "buttons": max_buttons
            }
        }]
    
    def _get_max_user_id(self, tg_chat_id: int) -> Optional[int]:
        """
        Получение MAX user_id из маппинга по Telegram chat_id
        
        Args:
            tg_chat_id: Telegram chat ID
        
        Returns:
            MAX user_id или None
        """
        if not self.chat_user_mapping:
            # Если маппинга нет, используем тот же ID
            return tg_chat_id
        
        max_user_id = self.chat_user_mapping.get(str(tg_chat_id))
        if max_user_id:
            try:
                return int(max_user_id)
            except ValueError:
                self.logger.error(f"Invalid MAX user_id in mapping: {max_user_id}")
                return None
        
        return None
    
    async def process_telegram_message(
        self,
        update: TelegramUpdate
    ) -> Optional[MaxSendMessageResponse]:
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
        
        # Получение MAX user_id
        max_user_id = self._get_max_user_id(message.chat.id)
        if not max_user_id:
            self.logger.error(f"No MAX user_id mapping for Telegram chat {message.chat.id}")
            await self.telegram_client.send_message(
                chat_id=message.chat.id,
                text="❌ Ошибка: не настроен маппинг чатов для отправки в MAX"
            )
            return None
        
        # Извлечение текста
        text = message.text or ""
        if not text:
            self.logger.debug("Message has no text, skipping")
            return None
        
        # Конвертация inline клавиатуры если есть
        attachments = None
        if hasattr(message, 'reply_markup') and message.reply_markup:
            attachments = self._convert_telegram_keyboard_to_max(message.reply_markup)
        
        # Определение формата текста (если есть entities, используем markdown)
        text_format = None
        if message.entities:
            text_format = TextFormat.MARKDOWN
        
        # Отправка в MAX
        try:
            response = await self.max_client.send_message(
                user_id=max_user_id,
                text=text,
                attachments=attachments,
                format=text_format,
                notify=True
            )
            self.logger.info(f"Message forwarded from Telegram chat {message.chat.id} to MAX user {max_user_id}")
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
