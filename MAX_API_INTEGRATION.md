# Интеграция с MAX Messenger API

## Дата обновления: 30 марта 2026

## Обзор изменений

Модуль интеграции с MAX Messenger был полностью переписан в соответствии с официальной документацией MAX API (https://dev.max.ru/docs-api).

## Ключевые изменения

### 1. Обновлен базовый URL API
- **Старый**: `https://api.max.ru/bot`
- **Новый**: `https://platform-api.max.ru`

### 2. Изменен метод аутентификации
- Токен теперь передается через заголовок `Authorization: <token>`
- Удалена поддержка передачи токена через query-параметры

### 3. Обновлены endpoints

#### Отправка сообщений
- **Endpoint**: `POST /messages`
- **Query параметры**: `user_id` или `chat_id`
- **Тело запроса**: JSON с полями `text`, `attachments`, `link`, `notify`, `format`

#### Получение обновлений (Long Polling)
- **Endpoint**: `GET /updates`
- **Параметры**: `limit`, `timeout`, `marker`, `types`
- **Ответ**: `{updates: [], marker: int}`

#### Информация о боте
- **Endpoint**: `GET /me`
- **Ответ**: Объект `User` с полями `user_id`, `name`, `username`, `is_bot`

### 4. Обновлены модели данных

#### MaxUser
```python
user_id: int          # ID пользователя
name: str             # Имя пользователя
username: str         # Username
is_bot: bool          # Является ли ботом
last_activity_time: int  # Время последней активности
```

#### MaxMessage
```python
sender: MaxUser       # Отправитель
recipient: MaxRecipient  # Получатель (user_id или chat_id)
timestamp: int        # Unix timestamp
body: MaxMessageBody  # Тело сообщения (text, attachments)
link: dict           # Связанное сообщение (reply/forward)
```

#### MaxUpdate
```python
update_type: str      # Тип обновления (message_created, message_callback, etc.)
timestamp: int        # Unix timestamp события
message: MaxMessage   # Сообщение
user_locale: str      # Язык пользователя (IETF BCP 47)
```

### 5. Поддержка Inline клавиатур

Реализована конвертация Telegram inline клавиатур в формат MAX:

**Поддерживаемые типы кнопок:**
- `callback` - отправляет событие `message_callback`
- `link` - открывает ссылку (до 2048 символов)
- `request_contact` - запрашивает контакт пользователя
- `request_geo_location` - запрашивает геолокацию
- `open_app` - открывает мини-приложение
- `message` - отправляет текстовое сообщение

**Ограничения:**
- До 210 кнопок всего
- До 30 рядов
- До 7 кнопок в ряду (до 3 для link/open_app/request_*)

**Пример:**
```python
attachments = [{
    "type": "inline_keyboard",
    "payload": {
        "buttons": [
            [
                {"type": "callback", "text": "Кнопка 1", "payload": "data1"},
                {"type": "link", "text": "Ссылка", "url": "https://example.com"}
            ]
        ]
    }
}]
```

### 6. Форматирование текста

Поддерживаются два формата:

#### Markdown
```python
format = TextFormat.MARKDOWN

# Поддерживаемые теги:
*курсив* или _курсив_
**жирный** или __жирный__
~~зачёркнутый~~
++подчёркнутый++
`моноширинный`
[ссылка](https://example.com)
[Упоминание](max://user/user_id)
```

#### HTML
```python
format = TextFormat.HTML

# Поддерживаемые теги:
<i> или <em> - курсив
<b> или <strong> - жирный
<del> или <s> - зачёркнутый
<ins> или <u> - подчёркнутый
<pre> или <code> - моноширинный
<a href="url">текст</a> - ссылка
<a href="max://user/user_id">Имя</a> - упоминание
```

### 7. Маппинг чатов

Обновлен формат маппинга для работы с числовыми ID:

```env
# Формат: {"telegram_chat_id": "max_user_id"}
CHAT_USER_MAPPING={"123456789": "987654321"}
```

**Важно:**
- Telegram chat_id - числовой ID чата в Telegram
- MAX user_id - числовой ID пользователя в MAX
- Оба значения должны быть числами

### 8. Long Polling

Обновлен механизм long polling:

**Параметры:**
- `limit`: 1-1000 (по умолчанию 100)
- `timeout`: 0-90 секунд (по умолчанию 30)
- `marker`: указатель на следующую страницу обновлений
- `types`: фильтр типов обновлений (например, `["message_created"]`)

**Особенности:**
- Используется `marker` вместо `offset`
- Маркер автоматически обновляется после каждого запроса
- Поддержка фильтрации по типам событий

## Использование

### Инициализация клиента

```python
from adapters.max import MaxClient

client = MaxClient(
    api_token="your_token_here",
    base_url="https://platform-api.max.ru",  # опционально
    timeout=30  # опционально
)
```

### Отправка сообщения

```python
# Простое текстовое сообщение
response = await client.send_message(
    user_id=123456789,
    text="Привет из Telegram!"
)

# С inline клавиатурой
response = await client.send_message(
    user_id=123456789,
    text="Выберите действие:",
    attachments=[{
        "type": "inline_keyboard",
        "payload": {
            "buttons": [[
                {"type": "callback", "text": "Кнопка", "payload": "action1"}
            ]]
        }
    }]
)

# С форматированием
response = await client.send_message(
    user_id=123456789,
    text="**Жирный текст** и *курсив*",
    format=TextFormat.MARKDOWN
)
```

### Получение обновлений

```python
# Long polling
marker = None
while True:
    updates_response = await client.get_updates(
        limit=100,
        timeout=60,
        marker=marker,
        types=["message_created"]
    )
    
    for update in updates_response.updates:
        # Обработка обновления
        print(update.message.body.text)
    
    # Обновление маркера
    marker = updates_response.marker
```

### Проверка здоровья API

```python
is_healthy = await client.health_check()
if is_healthy:
    print("MAX API доступен")
```

## Ограничения и рекомендации

### Rate Limiting
- Максимум 30 запросов в секунду (30 rps)
- Рекомендуется использовать exponential backoff при ошибках 429

### Размеры данных
- Текст сообщения: до 4000 символов
- URL в кнопке link: до 2048 символов
- Текст на кнопке: до 128 символов

### Режимы работы
- **Long Polling**: для разработки и тестирования
- **Webhook**: для production (только HTTPS, включая самоподписанные сертификаты)

### Webhook
Для настройки webhook используйте метод подписки:
```bash
POST /subscriptions
{
  "url": "https://your-domain.com/webhook",
  "update_types": ["message_created", "message_callback"]
}
```

## Миграция с предыдущей версии

### Изменения в конфигурации

**Удалены параметры:**
- `MAX_SEND_ENDPOINT`
- `MAX_RECEIVE_ENDPOINT`

**Изменены значения по умолчанию:**
- `MAX_API_BASE_URL`: `https://platform-api.max.ru`

### Изменения в коде

**Инициализация клиента:**
```python
# Старый способ
max_client = MaxClient(
    base_url=settings.max_api_base_url,
    api_token=settings.max_api_token,
    send_endpoint=settings.max_send_endpoint,
    receive_endpoint=settings.max_receive_endpoint
)

# Новый способ
max_client = MaxClient(
    api_token=settings.max_api_token,
    base_url=settings.max_api_base_url,
    timeout=settings.max_timeout
)
```

**Отправка сообщений:**
```python
# Старый способ
response = await client.send_message(
    MaxMessage(chat_id="123", text="Hello")
)

# Новый способ
response = await client.send_message(
    user_id=123,
    text="Hello"
)
```

## Troubleshooting

### Ошибка 401 Unauthorized
- Проверьте токен в настройках бота на платформе MAX
- Убедитесь, что токен передается в заголовке Authorization

### Ошибка 404 Not Found
- Проверьте правильность базового URL: `https://platform-api.max.ru`
- Убедитесь, что используете правильные endpoints

### Сообщения не доставляются
- Проверьте маппинг чатов в `CHAT_USER_MAPPING`
- Убедитесь, что MAX user_id существует и корректен
- Проверьте логи на наличие ошибок

### Long polling не работает
- Убедитесь, что `MAX_MODE=polling`
- Проверьте, что маркер обновляется корректно
- Увеличьте timeout если нужно

## Полезные ссылки

- [Документация MAX API](https://dev.max.ru/docs-api)
- [Методы API](https://dev.max.ru/docs-api/methods/POST/messages)
- [Объекты API](https://dev.max.ru/docs-api/objects/Message)
- [Платформа MAX для партнёров](https://business.max.ru/self)
