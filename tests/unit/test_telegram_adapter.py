"""
Unit tests for Telegram adapter
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from adapters.telegram import TelegramClient


class TestTelegramClient:
    """Tests for TelegramClient"""
    
    def test_client_initialization(self, telegram_bot_token):
        """Test client initialization"""
        client = TelegramClient(bot_token=telegram_bot_token)
        assert client.bot_token == telegram_bot_token
        assert f"bot{telegram_bot_token}" in client.base_url
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_context_manager(self, telegram_bot_token):
        """Test async context manager"""
        async with TelegramClient(bot_token=telegram_bot_token) as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)
        # Client should be closed after exiting context
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_telegram_client, telegram_api_response):
        """Test successful message sending"""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = telegram_api_response
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        # Send message
        result = await mock_telegram_client.send_message(
            chat_id=123456789,
            text="Test message"
        )
        
        assert result == telegram_api_response
        mock_telegram_client._client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_message_with_parse_mode(self, mock_telegram_client, telegram_api_response):
        """Test sending message with parse mode"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = telegram_api_response
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.send_message(
            chat_id=123456789,
            text="*Bold text*",
            parse_mode="Markdown"
        )
        
        assert result == telegram_api_response
        call_args = mock_telegram_client._client.post.call_args
        assert call_args[1]["json"]["parse_mode"] == "Markdown"
    
    @pytest.mark.asyncio
    async def test_send_message_with_reply(self, mock_telegram_client, telegram_api_response):
        """Test sending message as reply"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = telegram_api_response
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.send_message(
            chat_id=123456789,
            text="Reply message",
            reply_to_message_id=42
        )
        
        assert result == telegram_api_response
        call_args = mock_telegram_client._client.post.call_args
        assert call_args[1]["json"]["reply_to_message_id"] == 42
    
    @pytest.mark.asyncio
    async def test_send_message_http_error(self, mock_telegram_client):
        """Test send message with HTTP error"""
        mock_telegram_client._client.post = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        
        with pytest.raises(httpx.HTTPError):
            await mock_telegram_client.send_message(
                chat_id=123456789,
                text="Test message"
            )
    
    @pytest.mark.asyncio
    async def test_get_updates(self, mock_telegram_client):
        """Test getting updates"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "ok": True,
            "result": [
                {"update_id": 1, "message": {"text": "Hello"}},
                {"update_id": 2, "message": {"text": "World"}}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.get = AsyncMock(return_value=mock_response)
        
        updates = await mock_telegram_client.get_updates(offset=0, limit=10)
        
        assert len(updates) == 2
        assert updates[0]["update_id"] == 1
        assert updates[1]["update_id"] == 2
    
    @pytest.mark.asyncio
    async def test_get_updates_with_allowed_updates(self, mock_telegram_client):
        """Test getting updates with allowed_updates filter"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": []}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.get = AsyncMock(return_value=mock_response)
        
        await mock_telegram_client.get_updates(
            allowed_updates=["message", "edited_message"]
        )
        
        call_args = mock_telegram_client._client.get.call_args
        assert call_args[1]["params"]["allowed_updates"] == ["message", "edited_message"]
    
    @pytest.mark.asyncio
    async def test_set_webhook(self, mock_telegram_client):
        """Test setting webhook"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.set_webhook(
            url="https://example.com/webhook"
        )
        
        assert result["ok"] is True
        call_args = mock_telegram_client._client.post.call_args
        assert call_args[1]["json"]["url"] == "https://example.com/webhook"
    
    @pytest.mark.asyncio
    async def test_set_webhook_with_options(self, mock_telegram_client):
        """Test setting webhook with additional options"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        await mock_telegram_client.set_webhook(
            url="https://example.com/webhook",
            max_connections=100,
            allowed_updates=["message"]
        )
        
        call_args = mock_telegram_client._client.post.call_args
        assert call_args[1]["json"]["max_connections"] == 100
        assert call_args[1]["json"]["allowed_updates"] == ["message"]
    
    @pytest.mark.asyncio
    async def test_delete_webhook(self, mock_telegram_client):
        """Test deleting webhook"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.delete_webhook()
        
        assert result["ok"] is True
        mock_telegram_client._client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_me(self, mock_telegram_client):
        """Test getting bot info"""
        bot_info = {
            "id": 123456789,
            "is_bot": True,
            "first_name": "TestBot",
            "username": "test_bot"
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": bot_info}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.get = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.get_me()
        
        assert result == bot_info
        assert result["username"] == "test_bot"
    
    @pytest.mark.asyncio
    async def test_answer_callback_query(self, mock_telegram_client):
        """Test answering callback query"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True, "result": True}
        mock_response.raise_for_status = MagicMock()
        
        mock_telegram_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_telegram_client.answer_callback_query(
            callback_query_id="123456789",
            text="Button clicked!",
            show_alert=True
        )
        
        assert result["ok"] is True
        call_args = mock_telegram_client._client.post.call_args
        assert call_args[1]["json"]["callback_query_id"] == "123456789"
        assert call_args[1]["json"]["text"] == "Button clicked!"
        assert call_args[1]["json"]["show_alert"] is True
    
    @pytest.mark.asyncio
    async def test_close_client(self, telegram_bot_token):
        """Test closing client"""
        client = TelegramClient(bot_token=telegram_bot_token)
        mock_http_client = AsyncMock(spec=httpx.AsyncClient)
        client._client = mock_http_client
        
        await client.close()
        
        mock_http_client.aclose.assert_called_once()
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_get_client_creates_new(self, telegram_bot_token):
        """Test that _get_client creates new client if none exists"""
        client = TelegramClient(bot_token=telegram_bot_token)
        assert client._client is None
        
        http_client = client._get_client()
        
        assert http_client is not None
        assert isinstance(http_client, httpx.AsyncClient)
        assert client._client is http_client
