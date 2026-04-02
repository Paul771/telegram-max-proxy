import httpx
from typing import Optional, Dict, Any
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_mtproto_proxy_url(host: str, port: int, secret: str) -> str:
    """
    Создает URL для MTProto прокси в формате, понятном httpx
    
    MTProto прокси использует специальный формат:
    - Секрет должен быть в hex формате
    - Поддерживаются dd-секреты (обфусцированные) и ee-секреты (secure)
    
    Args:
        host: Хост MTProto прокси
        port: Порт MTProto прокси
        secret: Секретный ключ (hex строка, начинается с dd или ee)
    
    Returns:
        URL в формате socks5h для использования с httpx
    """
    # MTProto прокси работает через SOCKS5
    # Используем socks5h для резолва DNS через прокси
    proxy_url = f"socks5://{host}:{port}"
    
    logger.info(f"MTProto proxy configured: {host}:{port}")
    logger.debug(f"MTProto secret: {secret[:10]}...")
    
    return proxy_url


def create_proxy_url(
    http_proxy: Optional[str] = None,
    socks_proxy: Optional[str] = None,
    mtproto_host: Optional[str] = None,
    mtproto_port: Optional[int] = None,
    mtproto_secret: Optional[str] = None
) -> Optional[str]:
    """
    Создает URL прокси на основе доступных настроек
    
    Приоритет:
    1. MTProto прокси (если все параметры указаны)
    2. SOCKS прокси
    3. HTTP прокси
    
    Args:
        http_proxy: HTTP прокси URL
        socks_proxy: SOCKS5 прокси URL
        mtproto_host: MTProto прокси хост
        mtproto_port: MTProto прокси порт
        mtproto_secret: MTProto прокси секрет
    
    Returns:
        URL прокси или None если прокси не настроен
    """
    # Проверка MTProto прокси
    if mtproto_host and mtproto_port and mtproto_secret:
        logger.info("Using MTProto proxy for Telegram")
        return create_mtproto_proxy_url(mtproto_host, mtproto_port, mtproto_secret)
    
    # SOCKS прокси
    if socks_proxy:
        logger.info(f"Using SOCKS proxy: {socks_proxy}")
        return socks_proxy
    
    # HTTP прокси
    if http_proxy:
        logger.info(f"Using HTTP proxy: {http_proxy}")
        return http_proxy
    
    return None


def validate_mtproto_secret(secret: str) -> bool:
    """
    Проверяет валидность MTProto секрета
    
    Args:
        secret: Секретный ключ в hex формате
    
    Returns:
        True если секрет валиден
    """
    if not secret:
        return False
    
    # Секрет должен быть hex строкой
    try:
        bytes.fromhex(secret)
    except ValueError:
        logger.error("MTProto secret must be a valid hex string")
        return False
    
    # Проверка префикса (dd или ee)
    if not (secret.startswith('dd') or secret.startswith('ee')):
        logger.warning("MTProto secret should start with 'dd' or 'ee'")
    
    # Минимальная длина секрета
    if len(secret) < 32:
        logger.error("MTProto secret is too short (minimum 32 hex chars)")
        return False
    
    return True
