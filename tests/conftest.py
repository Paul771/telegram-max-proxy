"""
Pytest configuration and fixtures for telegram-max-proxy tests
"""
import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from services.proxy import ProxyService
from models.telegram import TelegramUpdate, TelegramMessage, TelegramChat, TelegramUser
from models.max import (
    MaxUpdate, MaxMessage, MaxUser, MaxRecipient, MaxMessageBody,
    MaxSendMessageResponse, MaxUpdatesResponse
)


# ============================================================================
# Fixtures for test data
# ============================================================================

@pytest.fixture
def telegram_bot_token() -> str:
    """Test Telegram bot token"""
    return "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"


@pytest.fixture
def max_api_token() -> str:
    """Test MAX API token"""
    return "test_max_token_12345"


@pytest.fixture
def chat_user_mapping() -> Dict[str, str]:
    """Test chat to user mapping"""
    return {
        "123456789": "987654321",
        "111111111": "222222222"
    }


# ============================================================================
# Fixtures for Telegram models
# ============================================================================

@pytest.fixture
def telegram_user() -> TelegramUser:
    """Sample Telegram user"""
    return TelegramUser(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="en"
    )


@pytest.fixture
def telegram_chat() -> TelegramChat:
    """Sample Telegram chat"""
    return TelegramChat(
        id=123456789,
        type="private",
        first_name="Test",
        username="testuser"
    )


@pytest.fixture
def telegram_message(telegram_user, telegram_chat) -> TelegramMessage:
    """Sample Telegram message"""
    return TelegramMessage(
        message_id=1,
        from_user=telegram_user,
        chat=telegram_chat,
        date=1234567890,
        text="Hello from Telegram"
    )


@pytest.fixture
def telegram_update(telegram_message) -> TelegramUpdate:
    """Sample Telegram update"""
    return TelegramUpdate(
        update_id=1,
        message=telegram_message
    )


# ============================================================================
# Fixtures for MAX models
# ============================================================================

@pytest.fixture
def max_user() -> MaxUser:
    """Sample MAX user"""
    return MaxUser(
        user_id=987654321,
        name="Test MAX User",
        username="maxuser",
        is_bot=False
    )


@pytest.fixture
def max_recipient() -> MaxRecipient:
    """Sample MAX recipient"""
    return MaxRecipient(
        user_id=987654321,
        chat_type="dialog"
    )


@pytest.fixture
def max_message_body() -> MaxMessageBody:
    """Sample MAX message body"""
    return MaxMessageBody(
        text="Hello from MAX"
    )


@pytest.fixture
def max_message(max_user, max_recipient, max_message_body) -> MaxMessage:
    """Sample MAX message"""
    return MaxMessage(
        sender=max_user,
        recipient=max_recipient,
        timestamp=1234567890,
        body=max_message_body
    )


@pytest.fixture
def max_update(max_message) -> MaxUpdate:
    """Sample MAX update"""
    return MaxUpdate(
        update_type="message_created",
        timestamp=1234567890,
        message=max_message
    )


@pytest.fixture
def max_send_response(max_message) -> MaxSendMessageResponse:
    """Sample MAX send message response"""
    return MaxSendMessageResponse(
        message=max_message
    )


# ============================================================================
# Fixtures for clients (mocked)
# ============================================================================

@pytest.fixture
def mock_telegram_client(telegram_bot_token) -> TelegramClient:
    """Mocked Telegram client"""
    client = TelegramClient(bot_token=telegram_bot_token)
    client._client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def mock_max_client(max_api_token) -> MaxClient:
    """Mocked MAX client"""
    client = MaxClient(api_token=max_api_token)
    client._client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def proxy_service(mock_telegram_client, mock_max_client, chat_user_mapping) -> ProxyService:
    """Proxy service with mocked clients"""
    return ProxyService(
        telegram_client=mock_telegram_client,
        max_client=mock_max_client,
        chat_user_mapping=chat_user_mapping
    )


# ============================================================================
# Fixtures for HTTP responses
# ============================================================================

@pytest.fixture
def telegram_api_response() -> Dict[str, Any]:
    """Sample Telegram API response"""
    return {
        "ok": True,
        "result": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "TestBot",
                "username": "test_bot"
            },
            "chat": {
                "id": 123456789,
                "type": "private",
                "username": "testuser"
            },
            "date": 1234567890,
            "text": "Response from bot"
        }
    }


@pytest.fixture
def max_api_response(max_message) -> Dict[str, Any]:
    """Sample MAX API response"""
    return {
        "message": max_message.model_dump()
    }


# ============================================================================
# Utility fixtures
# ============================================================================

@pytest.fixture
def mock_httpx_response():
    """Factory for creating mock httpx responses"""
    def _create_response(status_code: int = 200, json_data: Dict[str, Any] = None):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.raise_for_status = MagicMock()
        return response
    return _create_response


@pytest.fixture
async def cleanup_clients():
    """Cleanup fixture to close clients after tests"""
    clients = []
    
    def register(client):
        clients.append(client)
        return client
    
    yield register
    
    # Cleanup
    for client in clients:
        if hasattr(client, 'close'):
            await client.close()


# ============================================================================
# Environment fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch, telegram_bot_token, max_api_token):
    """Mock environment variables"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", telegram_bot_token)
    monkeypatch.setenv("MAX_API_TOKEN", max_api_token)
    monkeypatch.setenv("CHAT_USER_MAPPING", '{"123456789": "987654321"}')
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "8000")
    monkeypatch.setenv("LOG_LEVEL", "info")
