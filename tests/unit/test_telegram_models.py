"""
Unit tests for Telegram models
"""
import pytest
from pydantic import ValidationError

from models.telegram import (
    TelegramUser,
    TelegramChat,
    TelegramMessage,
    TelegramUpdate
)


class TestTelegramUser:
    """Tests for TelegramUser model"""
    
    def test_create_user_minimal(self):
        """Test creating user with minimal required fields"""
        user = TelegramUser(
            id=123456789,
            is_bot=False,
            first_name="Test"
        )
        assert user.id == 123456789
        assert user.is_bot is False
        assert user.first_name == "Test"
        assert user.last_name is None
        assert user.username is None
    
    def test_create_user_full(self):
        """Test creating user with all fields"""
        user = TelegramUser(
            id=123456789,
            is_bot=True,
            first_name="Test",
            last_name="Bot",
            username="testbot",
            language_code="en"
        )
        assert user.id == 123456789
        assert user.is_bot is True
        assert user.first_name == "Test"
        assert user.last_name == "Bot"
        assert user.username == "testbot"
        assert user.language_code == "en"
    
    def test_user_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            TelegramUser(is_bot=False)
    
    def test_user_invalid_id_type(self):
        """Test that invalid id type raises validation error"""
        with pytest.raises(ValidationError):
            TelegramUser(
                id="not_an_int",
                is_bot=False,
                first_name="Test"
            )


class TestTelegramChat:
    """Tests for TelegramChat model"""
    
    def test_create_private_chat(self):
        """Test creating private chat"""
        chat = TelegramChat(
            id=123456789,
            type="private",
            first_name="Test",
            username="testuser"
        )
        assert chat.id == 123456789
        assert chat.type == "private"
        assert chat.first_name == "Test"
        assert chat.username == "testuser"
        assert chat.title is None
    
    def test_create_group_chat(self):
        """Test creating group chat"""
        chat = TelegramChat(
            id=-123456789,
            type="group",
            title="Test Group"
        )
        assert chat.id == -123456789
        assert chat.type == "group"
        assert chat.title == "Test Group"
    
    def test_create_supergroup_chat(self):
        """Test creating supergroup chat"""
        chat = TelegramChat(
            id=-100123456789,
            type="supergroup",
            title="Test Supergroup",
            username="testsupergroup"
        )
        assert chat.id == -100123456789
        assert chat.type == "supergroup"
        assert chat.title == "Test Supergroup"
        assert chat.username == "testsupergroup"
    
    def test_create_channel(self):
        """Test creating channel"""
        chat = TelegramChat(
            id=-100987654321,
            type="channel",
            title="Test Channel",
            username="testchannel"
        )
        assert chat.id == -100987654321
        assert chat.type == "channel"
        assert chat.title == "Test Channel"
    
    def test_chat_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            TelegramChat(id=123)


class TestTelegramMessage:
    """Tests for TelegramMessage model"""
    
    def test_create_message_minimal(self, telegram_chat):
        """Test creating message with minimal fields"""
        message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890
        )
        assert message.message_id == 1
        assert message.chat == telegram_chat
        assert message.date == 1234567890
        assert message.text is None
        assert message.from_user is None
    
    def test_create_message_with_text(self, telegram_user, telegram_chat):
        """Test creating message with text"""
        message = TelegramMessage(
            message_id=1,
            from_user=telegram_user,
            chat=telegram_chat,
            date=1234567890,
            text="Hello, World!"
        )
        assert message.message_id == 1
        assert message.from_user == telegram_user
        assert message.chat == telegram_chat
        assert message.text == "Hello, World!"
    
    def test_create_message_with_entities(self, telegram_chat):
        """Test creating message with entities"""
        entities = [
            {"type": "bold", "offset": 0, "length": 5},
            {"type": "url", "offset": 6, "length": 20}
        ]
        message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890,
            text="Hello https://example.com",
            entities=entities
        )
        assert message.entities == entities
    
    def test_create_message_with_reply(self, telegram_chat):
        """Test creating message with reply_to_message"""
        original_message = TelegramMessage(
            message_id=1,
            chat=telegram_chat,
            date=1234567890,
            text="Original message"
        )
        reply_message = TelegramMessage(
            message_id=2,
            chat=telegram_chat,
            date=1234567891,
            text="Reply message",
            reply_to_message=original_message
        )
        assert reply_message.reply_to_message == original_message
        assert reply_message.reply_to_message.text == "Original message"
    
    def test_message_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            TelegramMessage(message_id=1)


class TestTelegramUpdate:
    """Tests for TelegramUpdate model"""
    
    def test_create_update_with_message(self, telegram_message):
        """Test creating update with message"""
        update = TelegramUpdate(
            update_id=1,
            message=telegram_message
        )
        assert update.update_id == 1
        assert update.message == telegram_message
        assert update.edited_message is None
    
    def test_create_update_with_edited_message(self, telegram_message):
        """Test creating update with edited message"""
        update = TelegramUpdate(
            update_id=2,
            edited_message=telegram_message
        )
        assert update.update_id == 2
        assert update.edited_message == telegram_message
        assert update.message is None
    
    def test_create_update_with_channel_post(self, telegram_message):
        """Test creating update with channel post"""
        update = TelegramUpdate(
            update_id=3,
            channel_post=telegram_message
        )
        assert update.update_id == 3
        assert update.channel_post == telegram_message
    
    def test_create_update_with_callback_query(self):
        """Test creating update with callback query"""
        callback_query = {
            "id": "123456789",
            "from": {"id": 123, "is_bot": False, "first_name": "Test"},
            "data": "button_clicked"
        }
        update = TelegramUpdate(
            update_id=4,
            callback_query=callback_query
        )
        assert update.update_id == 4
        assert update.callback_query == callback_query
    
    def test_create_empty_update(self):
        """Test creating update without any message types"""
        update = TelegramUpdate(update_id=5)
        assert update.update_id == 5
        assert update.message is None
        assert update.edited_message is None
        assert update.channel_post is None
    
    def test_update_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            TelegramUpdate()
    
    def test_update_serialization(self, telegram_update):
        """Test that update can be serialized and deserialized"""
        # Serialize to dict
        update_dict = telegram_update.model_dump()
        assert isinstance(update_dict, dict)
        assert update_dict["update_id"] == telegram_update.update_id
        
        # Deserialize from dict
        new_update = TelegramUpdate(**update_dict)
        assert new_update.update_id == telegram_update.update_id
        assert new_update.message.text == telegram_update.message.text
