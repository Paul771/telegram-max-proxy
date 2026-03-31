"""
Unit tests for ProxyService
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.proxy import ProxyService
from models.telegram import TelegramUpdate, TelegramMessage, TelegramChat, TelegramUser
from models.max import MaxSendMessageResponse, TextFormat


class TestProxyService:
    """Tests for ProxyService"""
    
    def test_service_initialization(self, mock_telegram_client, mock_max_client, chat_user_mapping):
        """Test service initialization"""
        service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client,
            chat_user_mapping=chat_user_mapping
        )
        assert service.telegram_client == mock_telegram_client
        assert service.max_client == mock_max_client
        assert service.chat_user_mapping == chat_user_mapping
    
    def test_service_initialization_without_mapping(self, mock_telegram_client, mock_max_client):
        """Test service initialization without chat mapping"""
        service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client
        )
        assert service.chat_user_mapping == {}
    
    def test_get_max_user_id_with_mapping(self, proxy_service):
        """Test getting MAX user_id from mapping"""
        max_user_id = proxy_service._get_max_user_id(123456789)
        assert max_user_id == 987654321
    
    def test_get_max_user_id_without_mapping(self, mock_telegram_client, mock_max_client):
        """Test getting MAX user_id without mapping (uses same ID)"""
        service = ProxyService(
            telegram_client=mock_telegram_client,
            max_client=mock_max_client,
            chat_user_mapping=None
        )
        max_user_id = service._get_max_user_id(123456789)
        assert max_user_id == 123456789
    
    def test_get_max_user_id_not_in_mapping(self, proxy_service):
        """Test getting MAX user_id for unmapped chat"""
        max_user_id = proxy_service._get_max_user_id(999999999)
        assert max_user_id is None
    
    def test_convert_telegram_keyboard_to_max_callback(self, proxy_service):
        """Test converting Telegram callback button to MAX format"""
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "Button 1", "callback_data": "action1"},
                    {"text": "Button 2", "callback_data": "action2"}
                ]
            ]
        }
        
        result = proxy_service._convert_telegram_keyboard_to_max(reply_markup)
        
        assert result is not None
        assert len(result) == 1
        assert result[0]["type"] == "inline_keyboard"
        assert len(result[0]["payload"]["buttons"]) == 1
        assert len(result[0]["payload"]["buttons"][0]) == 2
        assert result[0]["payload"]["buttons"][0][0]["type"] == "callback"
        assert result[0]["payload"]["buttons"][0][0]["text"] == "Button 1"
        assert result[0]["payload"]["buttons"][0][0]["payload"] == "action1"
    
    def test_convert_telegram_keyboard_to_max_link(self, proxy_service):
        """Test converting Telegram link button to MAX format"""
        reply_markup = {
            "inline_keyboard": [
                [{"text": "Visit site", "url": "https://example.com"}]
            ]
        }
        
        result = proxy_service._convert_telegram_keyboard_to_max(reply_markup)
        
        assert result is not None
        assert result[0]["payload"]["buttons"][0][0]["type"] == "link"
        assert result[0]["payload"]["buttons"][0][0]["url"] == "https://example.com"
    
    def test_convert_telegram_keyboard_mixed_buttons(self, proxy_service):
        """Test converting mixed button types"""
        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "Callback", "callback_data": "data"},
                    {"text": "Link", "url": "https://example.com"}
                ],
                [
                    {"text": "Another", "callback_data": "another"}
                ]
            ]
        }
        
        result = proxy_service._convert_telegram_keyboard_to_max(reply_markup)
        
        assert result is not None
        assert len(result[0]["payload"]["buttons"]) == 2
        assert len(result[0]["payload"]["buttons"][0]) == 2
        assert len(result[0]["payload"]["buttons"][1]) == 1
    
    def test_convert_telegram_keyboard_no_keyboard(self, proxy_service):
        """Test converting when no keyboard present"""
        result = proxy_service._convert_telegram_keyboard_to_max({})
        assert result is None
        
        result = proxy_service._convert_telegram_keyboard_to_max(None)
        assert result is None
    
    def test_convert_telegram_keyboard_empty_keyboard(self, proxy_service):
        """Test converting empty keyboard"""
        reply_markup = {"inline_keyboard": []}
        result = proxy_service._convert_telegram_keyboard_to_max(reply_markup)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_success(self, proxy_service, telegram_update, max_send_response):
        """Test successful message processing"""
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        result = await proxy_service.process_telegram_message(telegram_update)
        
        assert result == max_send_response
        proxy_service.max_client.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_no_message(self, proxy_service):
        """Test processing update without message"""
        update = TelegramUpdate(update_id=1)
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_from_bot(self, proxy_service, telegram_chat):
        """Test that bot messages are ignored"""
        bot_user = TelegramUser(
            id=123456789,
            is_bot=True,
            first_name="Bot"
        )
        message = TelegramMessage(
            message_id=1,
            from_user=bot_user,
            chat=telegram_chat,
            date=1234567890,
            text="Bot message"
        )
        update = TelegramUpdate(update_id=1, message=message)
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_no_text(self, proxy_service, telegram_chat):
        """Test processing message without text"""
        message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890
        )
        update = TelegramUpdate(update_id=1, message=message)
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_no_mapping(self, proxy_service, telegram_chat):
        """Test processing message with no MAX user mapping"""
        # Create message from unmapped chat
        message = TelegramMessage(
            message_id=1,
            chat=TelegramChat(id=999999999, type="private"),
            date=1234567890,
            text="Test message"
        )
        update = TelegramUpdate(update_id=1, message=message)
        
        proxy_service.telegram_client.send_message = AsyncMock()
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result is None
        # Should send error message to Telegram
        proxy_service.telegram_client.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_with_entities(self, proxy_service, telegram_update, max_send_response):
        """Test processing message with entities (should use markdown)"""
        telegram_update.message.entities = [{"type": "bold", "offset": 0, "length": 5}]
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        await proxy_service.process_telegram_message(telegram_update)
        
        call_args = proxy_service.max_client.send_message.call_args
        assert call_args[1]["format"] == TextFormat.MARKDOWN
    
    @pytest.mark.asyncio
    async def test_process_telegram_message_max_error(self, proxy_service, telegram_update):
        """Test handling MAX API error"""
        proxy_service.max_client.send_message = AsyncMock(
            side_effect=Exception("MAX API error")
        )
        proxy_service.telegram_client.send_message = AsyncMock()
        
        result = await proxy_service.process_telegram_message(telegram_update)
        
        assert result is None
        # Should send error notification to Telegram
        proxy_service.telegram_client.send_message.assert_called_once()
        call_args = proxy_service.telegram_client.send_message.call_args
        assert "Ошибка" in call_args[1]["text"]
    
    @pytest.mark.asyncio
    async def test_process_edited_message(self, proxy_service, telegram_message, max_send_response):
        """Test processing edited message"""
        update = TelegramUpdate(update_id=1, edited_message=telegram_message)
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result == max_send_response
    
    @pytest.mark.asyncio
    async def test_process_channel_post(self, proxy_service, telegram_message, max_send_response):
        """Test processing channel post"""
        update = TelegramUpdate(update_id=1, channel_post=telegram_message)
        proxy_service.max_client.send_message = AsyncMock(return_value=max_send_response)
        
        result = await proxy_service.process_telegram_message(update)
        
        assert result == max_send_response
    
    @pytest.mark.asyncio
    async def test_forward_to_telegram_success(self, proxy_service):
        """Test forwarding message to Telegram"""
        expected_response = {"ok": True, "result": {"message_id": 123}}
        proxy_service.telegram_client.send_message = AsyncMock(return_value=expected_response)
        
        result = await proxy_service.forward_to_telegram(
            text="Test message",
            tg_chat_id=123456789
        )
        
        assert result == expected_response
        proxy_service.telegram_client.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Test message",
            reply_to_message_id=None
        )
    
    @pytest.mark.asyncio
    async def test_forward_to_telegram_with_reply(self, proxy_service):
        """Test forwarding message to Telegram as reply"""
        expected_response = {"ok": True, "result": {"message_id": 124}}
        proxy_service.telegram_client.send_message = AsyncMock(return_value=expected_response)
        
        result = await proxy_service.forward_to_telegram(
            text="Reply message",
            tg_chat_id=123456789,
            reply_to_message_id=42
        )
        
        assert result == expected_response
        call_args = proxy_service.telegram_client.send_message.call_args
        assert call_args[1]["reply_to_message_id"] == 42
    
    @pytest.mark.asyncio
    async def test_forward_to_telegram_error(self, proxy_service):
        """Test handling error when forwarding to Telegram"""
        proxy_service.telegram_client.send_message = AsyncMock(
            side_effect=Exception("Telegram API error")
        )
        
        with pytest.raises(Exception, match="Telegram API error"):
            await proxy_service.forward_to_telegram(
                text="Test message",
                tg_chat_id=123456789
            )
