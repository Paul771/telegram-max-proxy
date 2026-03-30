import logging
import sys
from typing import Optional


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Настройка логгера для модуля
    
    Args:
        name: Имя логгера (обычно __name__)
        level: Уровень логирования (debug, info, warning, error)
    
    Returns:
        Настроенный логгер
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger
