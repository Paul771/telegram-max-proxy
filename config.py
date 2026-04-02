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
        default="https://platform-api.max.ru",
        description="Base URL for MAX API"
    )
    max_api_token: str = Field(..., min_length=1, description="MAX API bot token")
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
    
    # HTTP/SOCKS Proxy settings for Telegram API
    http_proxy: Optional[str] = Field(
        default=None,
        description="HTTP/HTTPS proxy URL (e.g., http://proxy.example.com:8080)"
    )
    socks_proxy: Optional[str] = Field(
        default=None,
        description="SOCKS5 proxy URL (e.g., socks5://proxy.example.com:1080)"
    )
    
    # MTProto Proxy settings for Telegram API
    mtproto_proxy_host: Optional[str] = Field(
        default=None,
        description="MTProto proxy host (e.g., proxy.example.com)"
    )
    mtproto_proxy_port: Optional[int] = Field(
        default=None,
        description="MTProto proxy port (e.g., 443)"
    )
    mtproto_proxy_secret: Optional[str] = Field(
        default=None,
        description="MTProto proxy secret (dd-secret, starts with 'dd' or 'ee')"
    )
    
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
