from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Telegram Bot API
    telegram_bot_token: str
    telegram_webhook_path: str = "/webhook/telegram"
    
    # MAX Messenger API
    # Базовый URL MAX API (по умолчанию https://api.max.ru/bot)
    max_api_base_url: str = "https://api.max.ru/bot"
    max_api_token: str
    max_send_endpoint: str = "/messages/send"
    max_receive_endpoint: str = "/updates/get"
    max_timeout: int = 30
    
    # Режим работы с MAX API
    # "webhook" - получать сообщения через webhook от Telegram и отправлять в MAX
    # "polling" - опрашивать MAX API через long polling и пересылать в Telegram
    max_mode: str = "webhook"
    
    # Proxy settings
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    
    # Optional: mapping configuration
    # Map Telegram chat_id to MAX user_id
    chat_user_mapping: Optional[dict] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
