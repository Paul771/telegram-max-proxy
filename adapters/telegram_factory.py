from typing import Union
from adapters.telegram import TelegramClient
from adapters.telegram_telethon import TelethonAdapter
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_telegram_client(
    mode: str,
    bot_token: str,
    api_id: int = None,
    api_hash: str = None,
    session_string: str = None,
    proxy_url: str = None,
    mtproto_proxy: dict = None
) -> Union[TelegramClient, TelethonAdapter]:
    """
    Фабрика для создания Telegram клиента
    
    Args:
        mode: Режим работы ('bot_api' или 'telethon')
        bot_token: Токен бота от @BotFather
        api_id: Telegram API ID (для telethon)
        api_hash: Telegram API Hash (для telethon)
        session_string: Строка сессии (для telethon)
        proxy_url: URL прокси для bot_api (http/socks5)
        mtproto_proxy: Настройки MTProto прокси для telethon
    
    Returns:
        Экземпляр TelegramClient или TelethonAdapter
    """
    
    if mode == "telethon":
        logger.info("Creating Telethon client (MTProto support)")
        
        if not api_id or not api_hash:
            raise ValueError(
                "Telethon mode requires TELEGRAM_API_ID and TELEGRAM_API_HASH. "
                "Get them from https://my.telegram.org"
            )
        
        return TelethonAdapter(
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            session_string=session_string,
            proxy=mtproto_proxy
        )
    
    elif mode == "bot_api":
        logger.info("Creating standard Bot API client")
        
        return TelegramClient(
            bot_token=bot_token,
            proxy_url=proxy_url
        )
    
    else:
        raise ValueError(f"Unknown telegram_mode: {mode}. Use 'bot_api' or 'telethon'")


def prepare_mtproto_proxy(host: str, port: int, secret: str) -> dict:
    """
    Подготовка настроек MTProto прокси для Telethon
    
    Args:
        host: Хост прокси
        port: Порт прокси
        secret: Секрет в hex формате
    
    Returns:
        Словарь с настройками прокси
    """
    return {
        'proxy_type': 'mtproto',
        'addr': host,
        'port': port,
        'secret': secret
    }
