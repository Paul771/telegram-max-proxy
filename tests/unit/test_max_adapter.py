"""
Unit tests for MAX adapter
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

from adapters.max import MaxClient
from models.max import MaxUser, MaxSendMessageResponse, MaxUpdatesResponse, TextFormat


class TestMaxClient:
    """Tests for MaxClient"""
    
    def test_client_initialization(self, max_api_token):
        """Test client initialization"""
        client = MaxClient(api_token=max_api_token)
        assert client.api_token == max_api_token
        assert client.base_url == "https://platform-api.max.ru"
        assert client._client is None
    
    def test_client_initialization_custom_base_url(self, max_api_token):
        """Test client initialization with custom base URL"""
        custom_url = "https://custom-api.max.ru"
        client = MaxClient(api_token=max_api_token, base_url=custom_url)
        assert client.base_url == custom_url
    
    def test_base_url_trailing_slash_removed(self, max_api_token):
        """Test that trailing slash is removed from base URL"""
        client = MaxClient(
            api_token=max_api_token,
            base_url="https://platform-api.max.ru/"
        )
        assert client.base_url == "https://platform-api.max.ru"
    
    @pytest.mark.asyncio
    async def test_context_manager(self, max_api_token):
        """Test async context manager"""
        async with MaxClient(api_token=max_api_token) as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)
    
    def test_get_headers(self, mock_max_client, max_api_token):
        """Test headers generation"""
        headers = mock_max_client._get_headers()
        assert headers["Authorization"] == max_api_token
        assert headers["Content-Type"] == "application/json"
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_max_client):
        """Test successful get_me request"""
        bot_data = {
            "user_id": 123456,
            "name": "Test Bot",
            "username": "testbot",
            "is_bot": True
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = bot_data
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.get_me()
        
        assert isinstance(result, MaxUser)
        assert result.user_id == 123456
        assert result.name == "Test Bot"
        assert result.is_bot is True
    
    @pytest.mark.asyncio
    async def test_get_me_http_error(self, mock_max_client):
        """Test get_me with HTTP error"""
        mock_max_client._client.get = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        
        with pytest.raises(httpx.HTTPError):
            await mock_max_client.get_me()
    
    @pytest.mark.asyncio
    async def test_send_message_to_user(self, mock_max_client, max_message):
        """Test sending message to user"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": max_message.model_dump()}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.send_message(
            user_id=987654321,
            text="Hello from test"
        )
        
        assert isinstance(result, MaxSendMessageResponse)
        assert result.message is not None
    
    @pytest.mark.asyncio
    async def test_send_message_to_chat(self, mock_max_client, max_message):
        """Test sending message to chat"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": max_message.model_dump()}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.post = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.send_message(
            chat_id=123456,
            text="Hello to chat"
        )
        
        assert isinstance(result, MaxSendMessageResponse)
        call_args = mock_max_client._client.post.call_args
        assert call_args[1]["params"]["chat_id"] == 123456
    
    @pytest.mark.asyncio
    async def test_send_message_with_format(self, mock_max_client, max_message):
        """Test sending message with text format"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": max_message.model_dump()}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.post = AsyncMock(return_value=mock_response)
        
        await mock_max_client.send_message(
            user_id=987654321,
            text="**Bold text**",
            format=TextFormat.MARKDOWN
        )
        
        call_args = mock_max_client._client.post.call_args
        assert call_args[1]["json"]["format"] == "markdown"
    
    @pytest.mark.asyncio
    async def test_send_message_with_attachments(self, mock_max_client, max_message):
        """Test sending message with attachments"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": max_message.model_dump()}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.post = AsyncMock(return_value=mock_response)
        
        attachments = [
            {
                "type": "inline_keyboard",
                "payload": {"buttons": [[{"text": "Click", "type": "callback"}]]}
            }
        ]
        
        await mock_max_client.send_message(
            user_id=987654321,
            text="Message with keyboard",
            attachments=attachments
        )
        
        call_args = mock_max_client._client.post.call_args
        assert call_args[1]["json"]["attachments"] == attachments
    
    @pytest.mark.asyncio
    async def test_send_message_without_recipient(self, mock_max_client):
        """Test that sending message without user_id or chat_id raises error"""
        with pytest.raises(ValueError, match="Either user_id or chat_id must be provided"):
            await mock_max_client.send_message(text="Test")
    
    @pytest.mark.asyncio
    async def test_send_message_with_notify_false(self, mock_max_client, max_message):
        """Test sending message with notify=False"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": max_message.model_dump()}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.post = AsyncMock(return_value=mock_response)
        
        await mock_max_client.send_message(
            user_id=987654321,
            text="Silent message",
            notify=False
        )
        
        call_args = mock_max_client._client.post.call_args
        assert call_args[1]["json"]["notify"] is False
    
    @pytest.mark.asyncio
    async def test_get_updates_success(self, mock_max_client, max_update):
        """Test successful get_updates request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "updates": [max_update.model_dump()],
            "marker": 123456
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.get_updates()
        
        assert isinstance(result, MaxUpdatesResponse)
        assert len(result.updates) == 1
        assert result.marker == 123456
    
    @pytest.mark.asyncio
    async def test_get_updates_with_params(self, mock_max_client):
        """Test get_updates with parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updates": [], "marker": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        await mock_max_client.get_updates(
            limit=50,
            timeout=60,
            marker=999,
            types=["message_created", "message_edited"]
        )
        
        call_args = mock_max_client._client.get.call_args
        params = call_args[1]["params"]
        assert params["limit"] == 50
        assert params["timeout"] == 60
        assert params["marker"] == 999
        assert params["types"] == "message_created,message_edited"
    
    @pytest.mark.asyncio
    async def test_get_updates_limit_boundaries(self, mock_max_client):
        """Test that get_updates enforces limit boundaries"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updates": [], "marker": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        # Test limit too low
        await mock_max_client.get_updates(limit=0)
        call_args = mock_max_client._client.get.call_args
        assert call_args[1]["params"]["limit"] == 1
        
        # Test limit too high
        await mock_max_client.get_updates(limit=2000)
        call_args = mock_max_client._client.get.call_args
        assert call_args[1]["params"]["limit"] == 1000
    
    @pytest.mark.asyncio
    async def test_get_updates_timeout_boundaries(self, mock_max_client):
        """Test that get_updates enforces timeout boundaries"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updates": [], "marker": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        # Test timeout too low
        await mock_max_client.get_updates(timeout=-5)
        call_args = mock_max_client._client.get.call_args
        assert call_args[1]["params"]["timeout"] == 0
        
        # Test timeout too high
        await mock_max_client.get_updates(timeout=100)
        call_args = mock_max_client._client.get.call_args
        assert call_args[1]["params"]["timeout"] == 90
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_max_client):
        """Test successful health check"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.health_check()
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_health_check_failure(self, mock_max_client):
        """Test failed health check"""
        mock_max_client._client.get = AsyncMock(
            side_effect=httpx.HTTPError("Connection failed")
        )
        
        result = await mock_max_client.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check_non_200_status(self, mock_max_client):
        """Test health check with non-200 status"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        
        mock_max_client._client.get = AsyncMock(return_value=mock_response)
        
        result = await mock_max_client.health_check()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_close_client(self, max_api_token):
        """Test closing client"""
        client = MaxClient(api_token=max_api_token)
        mock_http_client = AsyncMock(spec=httpx.AsyncClient)
        client._client = mock_http_client
        
        await client.close()
        
        mock_http_client.aclose.assert_called_once()
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_get_client_creates_new(self, max_api_token):
        """Test that _get_client creates new client if none exists"""
        client = MaxClient(api_token=max_api_token)
        assert client._client is None
        
        http_client = client._get_client()
        
        assert http_client is not None
        assert isinstance(http_client, httpx.AsyncClient)
        assert client._client is http_client
