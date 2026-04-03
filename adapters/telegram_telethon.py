from telethon import TelegramClient as TelethonClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from typing import Optional, Dict, Any, Callable
from utils.logger import setup_logger
import asyncio


class TelethonAdapter:
    """
    Адаптер для работы с Telegram через Telethon (MTProto)
    
    Этот адаптер позволяет использовать MTProto прокси для подключения к Telegram,
    что обходит блокировки Bot API.
    """
    
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        bot_token: str,
        session_string: Optional[str] = None,
        proxy: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализация Telethon клиента
        
        Args:
            api_id: Telegram API ID (получить на https://my.telegram.org)
            api_hash: Telegram API Hash
            bot_token: Токен бота от @BotFather
            session_string: Строка сессии для переиспользования
            proxy: Настройки MTProto прокси в формате:
                {
                    'proxy_type': 'mtproto',
                    'addr': 'proxy.example.com',
                    'port': 443,
                    'secret': 'dd1234567890abcdef...'
                }
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.proxy = proxy
        self.logger = setup_logger(__name__)
        
        # Создание сессии
        session = StringSession(session_string) if session_string else StringSession()
        
        # Создание клиента с прокси
        self.client = TelethonClient(
            session,
            self.api_id,
            self.api_hash,
            proxy=self._prepare_proxy() if proxy else None
        )
        
        self._message_handlers = []
        self._is_running = False
    
    def _prepare_proxy(self) -> Optional[tuple]:
        """
        Подготовка прокси для Telethon
        
        Returns:
            Кортеж (proxy_type, addr, port, secret) или None
        """
        if not self.proxy:
            return None
        
        proxy_type = self.proxy.get('proxy_type', 'mtproto')
        addr = self.proxy.get('addr')
        port = self.proxy.get('port')
        secret = self.proxy.get('secret')
        
        if not all([addr, port, secret]):
            self.logger.warning("Incomplete proxy configuration")
            return None
        
        # Telethon поддерживает MTProto прокси
        if proxy_type == 'mtproto':
            # Конвертируем hex secret в bytes
            if isinstance(secret, str):
                secret = bytes.fromhex(secret)
            
            return ('mtproto', addr, port, secret)
        
        # Также поддерживаются SOCKS5 и HTTP
        elif proxy_type == 'socks5':
            return ('socks5', addr, port)
        elif proxy_type == 'http':
            return ('http', addr, port)
        
        return None
    
    async def start(self):
        """Запуск клиента и авторизация как бот"""
        try:
            await self.client.start(bot_token=self.bot_token)
            self._is_running = True
            
            me = await self.client.get_me()
            self.logger.info(f"Telethon bot started: @{me.username}")
            
            # Получение строки сессии для сохранения
            session_string = self.client.session.save()
            self.logger.debug(f"Session string: {session_string[:20]}...")
            
            return session_string
        except Exception as e:
            self.logger.error(f"Failed to start Telethon client: {e}")
            raise
    
    async def stop(self):
        """Остановка клиента"""
        if self._is_running:
            await self.client.disconnect()
            self._is_running = False
            self.logger.info("Telethon client stopped")
    
    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: Optional[str] = None,
        reply_to_message_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Отправка сообщения
        
        Args:
            chat_id: ID чата или username
            text: Текст сообщения
            parse_mode: Режим парсинга ('markdown' или 'html')
            reply_to_message_id: ID сообщения для ответа
            **kwargs: Дополнительные параметры
        
        Returns:
            Словарь с информацией об отправленном сообщении
        """
        try:
            # Определение формата парсинга
            parse_mode_map = {
                'Markdown': 'md',
                'markdown': 'md',
                'HTML': 'html',
                'html': 'html'
            }
            formatting = parse_mode_map.get(parse_mode) if parse_mode else None
            
            # Отправка сообщения
            message = await self.client.send_message(
                entity=chat_id,
                message=text,
                parse_mode=formatting,
                reply_to=reply_to_message_id,
                **kwargs
            )
            
            self.logger.debug(f"Message sent to {chat_id} via Telethon")
            
            # Возвращаем в формате, совместимом с Bot API
            return {
                'ok': True,
                'result': {
                    'message_id': message.id,
                    'date': message.date.timestamp(),
                    'chat': {
                        'id': message.chat_id,
                        'type': 'private' if isinstance(message.peer_id, PeerUser) else 'group'
                    },
                    'text': message.text
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to send message via Telethon: {e}")
            raise
    
    async def get_me(self) -> Dict[str, Any]:
        """
        Получение информации о боте
        
        Returns:
            Словарь с информацией о боте
        """
        try:
            me = await self.client.get_me()
            
            return {
                'id': me.id,
                'is_bot': me.bot,
                'first_name': me.first_name,
                'username': me.username
            }
        except Exception as e:
            self.logger.error(f"Failed to get bot info via Telethon: {e}")
            raise
    
    def add_message_handler(self, handler: Callable):
        """
        Добавление обработчика входящих сообщений
        
        Args:
            handler: Async функция-обработчик
        """
        self._message_handlers.append(handler)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            """Обработчик новых сообщений"""
            try:
                # Конвертируем в формат, совместимый с Bot API
                update_data = {
                    'update_id': event.id,
                    'message': {
                        'message_id': event.id,
                        'date': event.date.timestamp(),
                        'chat': {
                            'id': event.chat_id,
                            'type': 'private' if event.is_private else 'group'
                        },
                        'text': event.text,
                        'from': {
                            'id': event.sender_id,
                            'is_bot': False
                        }
                    }
                }
                
                # Вызываем обработчик
                await handler(update_data)
            except Exception as e:
                self.logger.error(f"Error in message handler: {e}")
    
    async def run_until_disconnected(self):
        """Запуск клиента до отключения"""
        await self.client.run_until_disconnected()
    
    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 30,
        allowed_updates: Optional[list] = None
    ) -> list:
        """
        Получение обновлений (для совместимости с Bot API)
        
        Note: Telethon использует event-driven подход, поэтому этот метод
        возвращает пустой список. Используйте add_message_handler вместо этого.
        """
        self.logger.warning("get_updates not supported in Telethon mode. Use add_message_handler instead.")
        return []
    
    async def close(self):
        """Закрытие клиента"""
        await self.stop()
