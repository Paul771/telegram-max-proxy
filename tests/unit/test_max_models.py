"""
Unit tests for MAX models
"""
import pytest
from pydantic import ValidationError

from models.max import (
    TextFormat,
    ButtonType,
    MaxUser,
    MaxChat,
    MaxRecipient,
    InlineKeyboardButton,
    InlineKeyboardAttachment,
    MaxMessageLink,
    MaxNewMessageBody,
    MaxMessageBody,
    MaxMessage,
    MaxUpdate,
    MaxUpdatesResponse,
    MaxSendMessageResponse
)


class TestTextFormat:
    """Tests for TextFormat enum"""
    
    def test_text_format_values(self):
        """Test TextFormat enum values"""
        assert TextFormat.MARKDOWN == "markdown"
        assert TextFormat.HTML == "html"


class TestButtonType:
    """Tests for ButtonType enum"""
    
    def test_button_type_values(self):
        """Test ButtonType enum values"""
        assert ButtonType.CALLBACK == "callback"
        assert ButtonType.LINK == "link"
        assert ButtonType.REQUEST_CONTACT == "request_contact"
        assert ButtonType.REQUEST_GEO_LOCATION == "request_geo_location"
        assert ButtonType.OPEN_APP == "open_app"
        assert ButtonType.MESSAGE == "message"


class TestMaxUser:
    """Tests for MaxUser model"""
    
    def test_create_user_minimal(self):
        """Test creating user with minimal required fields"""
        user = MaxUser(
            user_id=987654321,
            name="Test User"
        )
        assert user.user_id == 987654321
        assert user.name == "Test User"
        assert user.username is None
        assert user.is_bot is False
        assert user.last_activity_time is None
    
    def test_create_user_full(self):
        """Test creating user with all fields"""
        user = MaxUser(
            user_id=987654321,
            name="Test User",
            username="testuser",
            is_bot=True,
            last_activity_time=1234567890
        )
        assert user.user_id == 987654321
        assert user.name == "Test User"
        assert user.username == "testuser"
        assert user.is_bot is True
        assert user.last_activity_time == 1234567890
    
    def test_user_missing_required_fields(self):
        """Test that missing required fields raise validation error"""
        with pytest.raises(ValidationError):
            MaxUser(user_id=123)


class TestMaxChat:
    """Tests for MaxChat model"""
    
    def test_create_dialog_chat(self):
        """Test creating dialog chat"""
        chat = MaxChat(
            chat_id=123456,
            type="dialog"
        )
        assert chat.chat_id == 123456
        assert chat.type == "dialog"
        assert chat.title is None
    
    def test_create_group_chat(self):
        """Test creating group chat"""
        chat = MaxChat(
            chat_id=789012,
            type="chat",
            title="Test Group",
            description="Test group description"
        )
        assert chat.chat_id == 789012
        assert chat.type == "chat"
        assert chat.title == "Test Group"
        assert chat.description == "Test group description"
    
    def test_create_channel(self):
        """Test creating channel"""
        chat = MaxChat(
            chat_id=345678,
            type="channel",
            title="Test Channel"
        )
        assert chat.chat_id == 345678
        assert chat.type == "channel"
        assert chat.title == "Test Channel"


class TestMaxRecipient:
    """Tests for MaxRecipient model"""
    
    def test_create_recipient_with_user_id(self):
        """Test creating recipient with user_id"""
        recipient = MaxRecipient(
            user_id=987654321,
            chat_type="dialog"
        )
        assert recipient.user_id == 987654321
        assert recipient.chat_type == "dialog"
        assert recipient.chat_id is None
    
    def test_create_recipient_with_chat_id(self):
        """Test creating recipient with chat_id"""
        recipient = MaxRecipient(
            chat_id=123456,
            chat_type="chat"
        )
        assert recipient.chat_id == 123456
        assert recipient.chat_type == "chat"
        assert recipient.user_id is None
    
    def test_create_empty_recipient(self):
        """Test creating recipient without ids"""
        recipient = MaxRecipient()
        assert recipient.user_id is None
        assert recipient.chat_id is None


class TestInlineKeyboardButton:
    """Tests for InlineKeyboardButton model"""
    
    def test_create_callback_button(self):
        """Test creating callback button"""
        button = InlineKeyboardButton(
            type=ButtonType.CALLBACK,
            text="Click me",
            payload="button_data"
        )
        assert button.type == ButtonType.CALLBACK
        assert button.text == "Click me"
        assert button.payload == "button_data"
        assert button.url is None
    
    def test_create_link_button(self):
        """Test creating link button"""
        button = InlineKeyboardButton(
            type=ButtonType.LINK,
            text="Visit site",
            url="https://example.com"
        )
        assert button.type == ButtonType.LINK
        assert button.text == "Visit site"
        assert button.url == "https://example.com"
        assert button.payload is None
    
    def test_button_text_max_length(self):
        """Test button text max length validation"""
        # Should work with 128 chars
        button = InlineKeyboardButton(
            type=ButtonType.CALLBACK,
            text="a" * 128,
            payload="data"
        )
        assert len(button.text) == 128
        
        # Should fail with more than 128 chars
        with pytest.raises(ValidationError):
            InlineKeyboardButton(
                type=ButtonType.CALLBACK,
                text="a" * 129,
                payload="data"
            )


class TestMaxMessageBody:
    """Tests for MaxMessageBody model"""
    
    def test_create_body_with_text(self):
        """Test creating message body with text"""
        body = MaxMessageBody(text="Hello, World!")
        assert body.text == "Hello, World!"
        assert body.attachments is None
    
    def test_create_body_with_attachments(self):
        """Test creating message body with attachments"""
        attachments = [{"type": "image", "url": "https://example.com/image.jpg"}]
        body = MaxMessageBody(
            text="Check this out",
            attachments=attachments
        )
        assert body.text == "Check this out"
        assert body.attachments == attachments
    
    def test_create_empty_body(self):
        """Test creating empty message body"""
        body = MaxMessageBody()
        assert body.text is None
        assert body.attachments is None


class TestMaxNewMessageBody:
    """Tests for MaxNewMessageBody model"""
    
    def test_create_new_message_body(self):
        """Test creating new message body"""
        body = MaxNewMessageBody(
            text="Hello from test",
            notify=True,
            format=TextFormat.MARKDOWN
        )
        assert body.text == "Hello from test"
        assert body.notify is True
        assert body.format == TextFormat.MARKDOWN
    
    def test_text_max_length(self):
        """Test text max length validation"""
        # Should work with 4000 chars
        body = MaxNewMessageBody(text="a" * 4000)
        assert len(body.text) == 4000
        
        # Should fail with more than 4000 chars
        with pytest.raises(ValidationError):
            MaxNewMessageBody(text="a" * 4001)
    
    def test_default_notify(self):
        """Test default notify value"""
        body = MaxNewMessageBody(text="Test")
        assert body.notify is True


class TestMaxMessage:
    """Tests for MaxMessage model"""
    
    def test_create_message(self, max_user, max_recipient, max_message_body):
        """Test creating MAX message"""
        message = MaxMessage(
            sender=max_user,
            recipient=max_recipient,
            timestamp=1234567890,
            body=max_message_body
        )
        assert message.sender == max_user
        assert message.recipient == max_recipient
        assert message.timestamp == 1234567890
        assert message.body == max_message_body
    
    def test_create_message_without_sender(self, max_recipient, max_message_body):
        """Test creating message without sender (bot message)"""
        message = MaxMessage(
            recipient=max_recipient,
            timestamp=1234567890,
            body=max_message_body
        )
        assert message.sender is None
        assert message.recipient == max_recipient


class TestMaxUpdate:
    """Tests for MaxUpdate model"""
    
    def test_create_update(self, max_message):
        """Test creating MAX update"""
        update = MaxUpdate(
            update_type="message_created",
            timestamp=1234567890,
            message=max_message
        )
        assert update.update_type == "message_created"
        assert update.timestamp == 1234567890
        assert update.message == max_message
    
    def test_create_update_without_message(self):
        """Test creating update without message"""
        update = MaxUpdate(
            update_type="user_joined",
            timestamp=1234567890
        )
        assert update.update_type == "user_joined"
        assert update.message is None


class TestMaxUpdatesResponse:
    """Tests for MaxUpdatesResponse model"""
    
    def test_create_updates_response(self, max_update):
        """Test creating updates response"""
        response = MaxUpdatesResponse(
            updates=[max_update],
            marker=123456
        )
        assert len(response.updates) == 1
        assert response.updates[0] == max_update
        assert response.marker == 123456
    
    def test_create_empty_updates_response(self):
        """Test creating empty updates response"""
        response = MaxUpdatesResponse()
        assert response.updates == []
        assert response.marker is None
    
    def test_create_updates_response_with_multiple_updates(self, max_message):
        """Test creating response with multiple updates"""
        updates = [
            MaxUpdate(update_type="message_created", timestamp=1, message=max_message),
            MaxUpdate(update_type="message_created", timestamp=2, message=max_message),
            MaxUpdate(update_type="message_created", timestamp=3, message=max_message)
        ]
        response = MaxUpdatesResponse(updates=updates, marker=999)
        assert len(response.updates) == 3
        assert response.marker == 999


class TestMaxSendMessageResponse:
    """Tests for MaxSendMessageResponse model"""
    
    def test_create_send_response(self, max_message):
        """Test creating send message response"""
        response = MaxSendMessageResponse(message=max_message)
        assert response.message == max_message
    
    def test_send_response_serialization(self, max_message):
        """Test send response serialization"""
        response = MaxSendMessageResponse(message=max_message)
        response_dict = response.model_dump()
        assert isinstance(response_dict, dict)
        assert "message" in response_dict
