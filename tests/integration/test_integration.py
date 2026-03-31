"""
Integration tests for telegram-max-proxy
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
import httpx

from main import app
from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from services.proxy import ProxyService
from models.telegram import TelegramUpdate, TelegramMessage, TelegramChat, TelegramUser
from models.max import MaxUpdate, MaxMessage, MaxUser, MaxRecipient, MaxMessageBody


@pytest.mark.integration
class TestEndToEndFlow:
    """End-to-end integration tests"""
    
    @pytest.mark.asyncio
    async def test_telegram_to_max_flow(self, mock_telegram_client, mock_max_client, chat_user_mapping):
        """Test complete flow from Telegram to MAX"""
        # Setup proxy service
        proxy_service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client,
            chat_user_mapping=chat_user_mapping
        )
        
        # Create Telegram update
        telegram_user = TelegramUser(
            id=123456789,
            is_bot=False,
            first_name="Test"
        )
        telegram_chat = TelegramChat(
            id=123456789,
            type="private"
        )
        telegram_message = TelegramMessage(
            message_id=1,
            from_user=telegram_user,
            chat=telegram_chat,
            date=1234567890,
            text="Hello from Telegram"
        )
        telegram_update = TelegramUpdate(
            update_id=1,
            message=telegram_message
        )
        
        # Mock MAX response
        max_message = MaxMessage(
            recipient=MaxRecipient(user_id=987654321),
            timestamp=1234567890,
            body=MaxMessageBody(text="Hello from Telegram")
        )
        from models.max import MaxSendMessageResponse
        max_response = MaxSendMessageResponse(message=max_message)
        
        mock_max_client.send_message = AsyncMock(return_value=max_response)
        
        # Process message
        result = await proxy_service.process_telegram_message(telegram_update)
        
        # Verify
        assert result is not None
        mock_max_client.send_message.assert_called_once()
        call_args = mock_max_client.send_message.call_args
        assert call_args[1]["user_id"] == 987654321
        assert call_args[1]["text"] == "Hello from Telegram"
    
    @pytest.mark.asyncio
    async def test_max_to_telegram_flow(self, mock_telegram_client, mock_max_client, chat_user_mapping):
        """Test complete flow from MAX to Telegram"""
        proxy_service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client,
            chat_user_mapping=chat_user_mapping
        )
        
        # Mock Telegram response
        telegram_response = {
            "ok": True,
            "result": {
                "message_id": 1,
                "text": "Hello from MAX"
            }
        }
        mock_telegram_client.send_message = AsyncMock(return_value=telegram_response)
        
        # Forward message
        result = await proxy_service.forward_to_telegram(
            text="Hello from MAX",
            tg_chat_id=123456789
        )
        
        # Verify
        assert result == telegram_response
        mock_telegram_client.send_message.assert_called_once()
        call_args = mock_telegram_client.send_message.call_args
        assert call_args[1]["chat_id"] == 123456789
        assert call_args[1]["text"] == "Hello from MAX"


@pytest.mark.integration
class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Telegram → MAX Messenger Proxy"
        assert data["status"] == "running"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        client = TestClient(app)
        
        with patch("main.telegram_client") as mock_tg, \
             patch("main.max_client") as mock_max:
            
            # Mock successful health checks
            mock_tg.get_me = AsyncMock(return_value={"id": 123, "username": "bot"})
            mock_max.health_check = AsyncMock(return_value=True)
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "telegram_api" in data
            assert "max_api" in data


@pytest.mark.integration
class TestClientIntegration:
    """Integration tests for client interactions"""
    
    @pytest.mark.asyncio
    async def test_telegram_client_lifecycle(self, telegram_bot_token):
        """Test Telegram client lifecycle"""
        async with TelegramClient(bot_token=telegram_bot_token) as client:
            assert client._client is not None
            
            # Mock HTTP response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "ok": True,
                "result": {"id": 123, "username": "bot"}
            }
            mock_response.raise_for_status = MagicMock()
            
            client._client.get = AsyncMock(return_value=mock_response)
            
            # Test get_me
            result = await client.get_me()
            assert result["username"] == "bot"
    
    @pytest.mark.asyncio
    async def test_max_client_lifecycle(self, max_api_token):
        """Test MAX client lifecycle"""
        async with MaxClient(api_token=max_api_token) as client:
            assert client._client is not None
            
            # Mock HTTP response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user_id": 123,
                "name": "Test Bot",
                "is_bot": True
            }
            mock_response.raise_for_status = MagicMock()
            
            client._client.get = AsyncMock(return_value=mock_response)
            
            # Test get_me
            result = await client.get_me()
            assert result.name == "Test Bot"
    
    @pytest.mark.asyncio
    async def test_proxy_service_with_real_clients(self, telegram_bot_token, max_api_token, chat_user_mapping):
        """Test proxy service with real client instances"""
        telegram_client = TelegramClient(bot_token=telegram_bot_token)
        max_client = MaxClient(api_token=max_api_token)
        
        proxy_service = ProxyService(
            telegram_client=telegram_client,
            max_client=max_client,
            chat_user_mapping=chat_user_mapping
        )
        
        assert proxy_service.telegram_client == telegram_client
        assert proxy_service.max_client == max_client
        assert proxy_service.chat_user_mapping == chat_user_mapping
        
        # Cleanup
        await telegram_client.close()
        await max_client.close()


@pytest.mark.integration
class TestErrorHandling:
    """Integration tests for error handling"""
    
    @pytest.mark.asyncio
    async def test_telegram_api_error_handling(self, mock_telegram_client, mock_max_client, chat_user_mapping):
        """Test handling of Telegram API errors"""
        proxy_service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client,
            chat_user_mapping=chat_user_mapping
        )
        
        # Mock Telegram error
        mock_telegram_client.send_message = AsyncMock(
            side_effect=httpx.HTTPError("Telegram API error")
        )
        
        with pytest.raises(httpx.HTTPError):
            await proxy_service.forward_to_telegram(
                text="Test",
                tg_chat_id=123456789
            )
    
    @pytest.mark.asyncio
    async def test_max_api_error_handling(self, proxy_service, telegram_update):
        """Test handling of MAX API errors"""
        # Mock MAX error
        proxy_service.max_client.send_message = AsyncMock(
            side_effect=httpx.HTTPError("MAX API error")
        )
        proxy_service.telegram_client.send_message = AsyncMock()
        
        result = await proxy_service.process_telegram_message(telegram_update)
        
        # Should return None and send error notification
        assert result is None
        proxy_service.telegram_client.send_message.assert_called_once()


@pytest.mark.integration
class TestMessageTransformation:
    """Integration tests for message transformation"""
    
    @pytest.mark.asyncio
    async def test_keyboard_transformation(self, proxy_service, telegram_chat, max_send_response):
        """Test inline keyboard transformation from Telegram to MAX"""
        # Create message with inline keyboard
        message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890,
            text="Choose option:"
        )
        
        # Add keyboard (simulating reply_markup)
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "Option 1", "callback_data": "opt1"},
                    {"text": "Option 2", "callback_data": "opt2"}
                ],
                [
                    {"text": "Visit", "url": "https://example.com"}
                ]
            ]
        }
        
        update = TelegramUpdate(update_id=1, message=message)
        
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        # Convert keyboard
        attachments = proxy_service._convert_telegram_keyboard_to_max(reply_markup)
        
        # Verify transformation
        assert attachments is not None
        assert len(attachments) == 1
        assert attachments[0]["type"] == "inline_keyboard"
        buttons = attachments[0]["payload"]["buttons"]
        assert len(buttons) == 2
        assert buttons[0][0]["type"] == "callback"
        assert buttons[0][1]["type"] == "callback"
        assert buttons[1][0]["type"] == "link"
    
    @pytest.mark.asyncio
    async def test_text_format_transformation(self, proxy_service, telegram_chat, max_send_response):
        """Test text format transformation"""
        # Message with entities (should trigger markdown format)
        message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890,
            text="**Bold** text",
            entities=[{"type": "bold", "offset": 0, "length": 6}]
        )
        update = TelegramUpdate(update_id=1, message=message)
        
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        await proxy_service.process_telegram_message(update)
        
        # Verify markdown format was used
        call_args = proxy_service.max_client.send_message.call_args
        from models.max import TextFormat
        assert call_args[1]["format"] == TextFormat.MARKDOWN


@pytest.mark.integration
@pytest.mark.slow
class TestConcurrency:
    """Integration tests for concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_multiple_messages_concurrent(self, proxy_service, telegram_chat, max_send_response):
        """Test processing multiple messages concurrently"""
        import asyncio
        
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        # Create multiple updates
        updates = []
        for i in range(5):
            message = TelegramMessage(
                message_id=i,
                chat=telegram_chat,
                date=1234567890 + i,
                text=f"Message {i}"
            )
            updates.append(TelegramUpdate(update_id=i, message=message))
        
        # Process concurrently
        tasks = [
            proxy_service.process_telegram_message(update)
            for update in updates
        ]
        results = await asyncio.gather(*tasks)
        
        # Verify all processed
        assert len(results) == 5
        assert all(r is not None for r in results)
        assert proxy_service.max_client.send_message.call_count == 5
