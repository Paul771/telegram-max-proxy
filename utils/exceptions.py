"""Пользовательские исключения для приложения"""


class ProxyError(Exception):
    """Базовое исключение для ошибок прокси"""
    pass


class TelegramAPIError(ProxyError):
    """Ошибка при работе с Telegram API"""
    pass


class MaxAPIError(ProxyError):
    """Ошибка при работе с MAX API"""
    pass


class ConfigurationError(ProxyError):
    """Ошибка конфигурации"""
    pass


class MappingError(ProxyError):
    """Ошибка маппинга чатов"""
    pass


class MessageForwardError(ProxyError):
    """Ошибка при пересылке сообщения"""
    pass
