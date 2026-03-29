# Telegram → MAX Messenger Proxy

Прокси-сервис для передачи сообщений между Telegram Bot API и MAX Messenger API.

## Структура проекта

```
telegram-max-proxy/
├── main.py              # FastAPI приложение
├── config.py            # Конфигурация
├── .env.example         # Шаблон конфигурации
├── requirements.txt     # Зависимости Python
├── README.md            # Документация
├── adapters/
│   ├── telegram.py      # Telegram Bot API клиент
│   └── max.py           # MAX Messenger API адаптер
├── services/
│   └── proxy.py         # Логика проксирования
└── models/
    ├── telegram.py      # Модели Telegram
    └── max.py           # Модели MAX
```

## Установка

### 1. Создайте виртуальное окружение

```bash
python -m venv venv
```

### 2. Активируйте виртуальное окружение

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Настройте переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
copy .env.example .env
```

**Обязательные параметры:**

| Переменная | Описание |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от @BotFather |
| `MAX_API_TOKEN` | Токен бота MAX (из личного кабинета MAX) |

**Опциональные параметры:**

| Переменная | По умолчанию | Описание |
|------------|--------------|----------|
| `MAX_API_BASE_URL` | `https://api.max.ru/bot` | Базовый URL MAX API |
| `MAX_SEND_ENDPOINT` | `/messages/send` | Endpoint отправки сообщений |
| `MAX_RECEIVE_ENDPOINT` | `/updates/get` | Endpoint получения сообщений |
| `MAX_MODE` | `webhook` | Режим: `webhook` или `polling` |
| `HOST` | `0.0.0.0` | Адрес хоста |
| `PORT` | `8000` | Порт |
| `LOG_LEVEL` | `info` | Уровень логирования |

## Запуск

### Режим разработки (с автоперезагрузкой)

```bash
python main.py
```

или

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Продакшен режим

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Режимы работы

### Webhook режим (по умолчанию)

Telegram отправляет сообщения на ваш сервер через webhook, сервис пересылает их в MAX.

**Настройка:**
```env
MAX_MODE=webhook
```

**Установка webhook в Telegram:**
```bash
curl -X POST "http://localhost:8000/webhook/set?webhook_url=https://your-domain.com/webhook/telegram"
```

### Polling режим

Сервис опрашивает MAX API через long polling и пересылает сообщения в Telegram.

**Настройка:**
```env
MAX_MODE=polling
```

**Требуется маппинг чатов:**
```env
CHAT_USER_MAPPING={"max_chat_1": "123456789", "max_chat_2": "987654321"}
```

Где ключ — ID чата в MAX, значение — Telegram chat_id.

## API Endpoints

### Веб-интерфейс документации

Откройте в браузере: `http://localhost:8000/docs`

### Основные endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/` | Информация о сервисе |
| `GET` | `/health` | Проверка здоровья |
| `POST` | `/webhook/telegram` | Webhook от Telegram |
| `POST` | `/telegram/send` | Отправка в Telegram |
| `POST` | `/webhook/set` | Установка webhook Telegram |
| `POST` | `/webhook/delete` | Удаление webhook Telegram |
| `GET` | `/bot/info` | Информация о Telegram боте |

## Интеграция с MAX API

### Получение токена бота MAX

1. Создайте бота в MAX Messenger через личный кабинет
2. Получите токен бота
3. Укажите в `.env` как `MAX_API_TOKEN`

### Настройка endpoints

MAX API может использовать различные endpoints. Проверьте документацию:
- https://dev.max.ru/docs/chatbots/bots-coding/hellobot/go

**Пример настройки в `.env`:**
```env
MAX_API_BASE_URL=https://api.max.ru/bot
MAX_SEND_ENDPOINT=/messages/send
MAX_RECEIVE_ENDPOINT=/updates/get
```

### Маппинг сообщений

Адаптер MAX (`adapters/max.py`) использует формат, похожий на Telegram API:

**Отправка сообщения:**
```json
POST /bot<token>/messages/send
{
  "chat_id": "user123",
  "text": "Привет!",
  "reply_to_message_id": "msg456"
}
```

**Получение обновлений:**
```json
GET /bot<token>/updates/get?limit=100&timeout=60

Ответ:
{
  "result": [
    {
      "message_id": "123",
      "from": {"id": "user123", "username": "user"},
      "chat": {"id": "chat123", "type": "private"},
      "date": 1234567890,
      "text": "Привет!"
    }
  ]
}
```

Если формат MAX API отличается, отредактируйте `adapters/max.py`.

## Маппинг чатов

Для сопоставления Telegram chat_id с MAX user_id используйте `chat_user_mapping`:

**В `.env`:**
```env
CHAT_USER_MAPPING={"123456789": "max_user_1", "987654321": "max_user_2"}
```

**Или в `config.py`:**
```python
chat_user_mapping = {
    "123456789": "max_user_1",
    "987654321": "max_user_2",
}
```

## Отладка

### Проверка подключения

```bash
# Проверка здоровья сервиса
curl http://localhost:8000/health

# Информация о Telegram боте
curl http://localhost:8000/bot/info

# Тестовая отправка в Telegram
curl -X POST http://localhost:8000/telegram/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id": 123456789, "text": "Тест"}'
```

### Логи

При запуске в режиме разработки (`--reload`) логи выводятся в консоль.

**Уровни логирования:**
- `debug` — подробная отладочная информация
- `info` — стандартная информация
- `warning` — только предупреждения и ошибки
- `error` — только ошибки

## Docker (опционально)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Сборка и запуск

```bash
docker build -t telegram-max-proxy .
docker run -p 8000:8000 --env-file .env telegram-max-proxy
```

### Docker Compose

```yaml
version: '3.8'

services:
  proxy:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

## Возможные проблемы

### 1. Ошибка аутентификации MAX API

**Проблема:** `401 Unauthorized`

**Решение:**
- Проверьте токен в `MAX_API_TOKEN`
- Убедитесь, что токен активен в личном кабинете MAX

### 2. Сообщения не отправляются в MAX

**Проблема:** Ошибка при отправке

**Решение:**
- Проверьте `MAX_API_BASE_URL` и endpoints
- Убедитесь, что формат запроса соответствует документации MAX
- Проверьте логи сервиса

### 3. Polling режим не работает

**Проблема:** Сообщения из MAX не приходят

**Решение:**
- Установите `MAX_MODE=polling`
- Настройте `CHAT_USER_MAPPING`
- Проверьте доступность MAX API через `/health`

## Лицензия

MIT
