"""Константы приложения"""

# HTTP timeouts
DEFAULT_HTTP_TIMEOUT = 30
LONG_POLLING_TIMEOUT = 60
HEALTH_CHECK_TIMEOUT = 10

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5
RETRY_BACKOFF = 2

# Polling settings
POLLING_ERROR_DELAY = 5
POLLING_EMPTY_DELAY = 1
DEFAULT_UPDATES_LIMIT = 100

# API endpoints
TELEGRAM_API_BASE = "https://api.telegram.org/bot"

# Message types
MESSAGE_TYPE_TEXT = "text"
MESSAGE_TYPE_IMAGE = "image"
MESSAGE_TYPE_VIDEO = "video"

# Chat types
CHAT_TYPE_PRIVATE = "private"
CHAT_TYPE_GROUP = "group"
CHAT_TYPE_SUPERGROUP = "supergroup"
CHAT_TYPE_CHANNEL = "channel"

# Service status
STATUS_RUNNING = "running"
STATUS_HEALTHY = "healthy"
STATUS_DEGRADED = "degraded"
STATUS_CONNECTED = "connected"
STATUS_DISCONNECTED = "disconnected"

# Response messages
MSG_SERVICE_NOT_INITIALIZED = "Service not initialized"
MSG_CLIENT_NOT_INITIALIZED = "Client not initialized"
MSG_ERROR_PROCESSING = "Error processing message"
MSG_ERROR_SENDING = "Error sending message"
