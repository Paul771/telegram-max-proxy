from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from typing import Optional, Literal
import json


class Settings(BaseSettings):
    # Telegram Bot API
    telegram_bot_token: str = Field(..., min_length=1, description="Telegram bot token from @BotFather")
    telegram_webhook_path: str = Field(default="/webhook/telegram", pattern="^/.*")
    
    # MAX Messenger API
    max_api_base_url: str = Field(
        default="https://api.max.ru/bot",
        description="Base URL for MAX API"
    )
    max_api_token: str = Field(..., min_length=1, description="MAX API bot token")
    max_send_endpoint: str = Field(default="/messages/send")
    max_receive_endpoint: str = Field(default="/updates/get")
    max_timeout: int = Field(default=30, ge=1, le=300)
    
    # Режим работы с MAX API
    max_mode: Literal["webhook", "polling"] = Field(
        default="webhook",
        description="Mode: 'webhook' or 'polling'"
    )
    
    # Proxy settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    log_level: Literal["debug", "info", "warning", "error"] = Field(default="info")
    
    # Optional: mapping configuration
    chat_user_mapping: Optional[dict] = Field(
        default=None,
        description="Map Telegram chat_id to MAX user_id"
    )
    
    @field_validator("chat_user_mapping", mode="before")
    @classmethod
    def parse_chat_mapping(cls, v):
        """Parse chat mapping from JSON string if needed"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("chat_user_mapping must be valid JSON")
        return v
    
    @field_validator("max_api_base_url")
    @classmethod
    def validate_base_url(cls, v):
        """Ensure base URL doesn't end with slash"""
        return v.rstrip("/")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
