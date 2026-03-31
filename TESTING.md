# Инструкция по тестированию telegram-max-proxy

## Текущий статус

✅ Python 3.12.1 установлен
✅ Виртуальное окружение создано
✅ Все зависимости установлены
✅ Файл .env создан

## Что нужно для тестирования

### 1. Получение токенов

#### Telegram Bot Token
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям (укажите имя и username бота)
4. Скопируйте полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### MAX Bot Token
1. Зарегистрируйтесь на [платформе MAX для партнёров](https://business.max.ru/self)
2. Создайте организацию и пройдите верификацию
3. Перейдите в раздел **Чат-боты** → **Создать бота**
4. После создания бота перейдите в **Интеграция** → **Получить токен**
5. Скопируйте токен

### 2. Настройка маппинга чатов

Для работы прокси необходимо настроить соответствие между Telegram и MAX:

#### Получение Telegram chat_id
1. Напишите боту в Telegram любое сообщение
2. Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Найдите поле `"chat":{"id":123456789}` - это ваш chat_id

#### Получение MAX user_id
1. Откройте MAX Messenger
2. Найдите вашего бота и напишите ему
3. На платформе MAX для партнёров в разделе бота посмотрите логи или используйте API
4. Или используйте метод `GET /me` для получения информации о боте

### 3. Настройка .env файла

Откройте файл `.env` и заполните следующие параметры:

```env
# Telegram Bot API
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# MAX Messenger API
MAX_API_TOKEN=your_max_bot_token_here

# Маппинг чатов (JSON формат)
# Формат: {"telegram_chat_id": "max_user_id"}
CHAT_USER_MAPPING={"123456789": "987654321"}

# Остальные параметры можно оставить по умолчанию
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
MAX_MODE=webhook
```

**Важно:**
- Замените `TELEGRAM_BOT_TOKEN` на ваш токен от BotFather
- Замените `MAX_API_TOKEN` на ваш токен от MAX
- В `CHAT_USER_MAPPING` укажите соответствие ваших ID

## Запуск приложения

### Вариант 1: Режим разработки (с автоперезагрузкой)

```powershell
# Активируйте виртуальное окружение
.\venv\Scripts\Activate.ps1

# Запустите приложение
python main.py
```

### Вариант 2: Через uvicorn

```powershell
# Активируйте виртуальное окружение
.\venv\Scripts\Activate.ps1

# Запустите с uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Вариант 3: Production режим

```powershell
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Проверка работы

### 1. Проверка запуска

После запуска вы должны увидеть:
```
INFO:     Started server process
INFO:     Waiting for application startup.
2026-03-30 14:37:13 - __main__ - INFO - Starting Telegram → MAX Messenger Proxy
2026-03-30 14:37:13 - __main__ - INFO - ✓ Telegram bot connected: @your_bot_name
2026-03-30 14:37:13 - __main__ - INFO - ✓ MAX API is available
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Проверка API endpoints

Откройте в браузере:
- **Документация API**: http://localhost:8000/docs
- **Информация о сервисе**: http://localhost:8000/
- **Health check**: http://localhost:8000/health

### 3. Настройка Telegram webhook

Для работы в webhook режиме (рекомендуется для production):

```bash
# Если у вас есть публичный домен с HTTPS
curl -X POST "http://localhost:8000/webhook/set?webhook_url=https://your-domain.com/webhook/telegram"
```

**Для локального тестирования** используйте ngrok или аналогичный сервис:
```bash
# Установите ngrok
# Запустите туннель
ngrok http 8000

# Используйте полученный URL для webhook
curl -X POST "http://localhost:8000/webhook/set?webhook_url=https://abc123.ngrok.io/webhook/telegram"
```

### 4. Тестирование отправки сообщений

#### Telegram → MAX

1. Напишите сообщение вашему Telegram боту
2. Проверьте логи приложения - должно появиться:
   ```
   INFO - Message forwarded from Telegram chat 123456789 to MAX user 987654321
   ```
3. Проверьте MAX Messenger - сообщение должно прийти от бота

#### MAX → Telegram (в режиме polling)

1. Измените в `.env`: `MAX_MODE=polling`
2. Перезапустите приложение
3. Напишите боту в MAX Messenger
4. Сообщение должно прийти в Telegram

### 5. Тестирование inline клавиатур

Отправьте боту в Telegram сообщение с inline клавиатурой:

```python
# Пример через Telegram Bot API
import requests

url = f"https://api.telegram.org/bot{YOUR_TOKEN}/sendMessage"
data = {
    "chat_id": YOUR_CHAT_ID,
    "text": "Выберите действие:",
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "Кнопка 1", "callback_data": "action1"},
                {"text": "Кнопка 2", "callback_data": "action2"}
            ],
            [
                {"text": "Ссылка", "url": "https://example.com"}
            ]
        ]
    }
}
requests.post(url, json=data)
```

Клавиатура должна корректно отобразиться в MAX.

## Troubleshooting

### Ошибка: "Service not initialized"
- Проверьте, что токены указаны правильно в `.env`
- Проверьте логи при запуске - должны быть галочки ✓

### Ошибка: "No MAX user_id mapping"
- Проверьте `CHAT_USER_MAPPING` в `.env`
- Убедитесь, что формат JSON корректный
- ID должны быть в кавычках: `{"123": "456"}`

### Ошибка: "Failed to connect to Telegram"
- Проверьте токен Telegram бота
- Проверьте интернет-соединение
- Убедитесь, что токен не содержит лишних пробелов

### Ошибка: "MAX API is not available"
- Проверьте токен MAX бота
- Убедитесь, что бот создан и активен на платформе MAX
- Проверьте, что `MAX_API_BASE_URL=https://platform-api.max.ru`

### Сообщения не доставляются
- Проверьте маппинг чатов
- Проверьте логи на наличие ошибок
- Убедитесь, что оба бота активны
- Для webhook режима проверьте, что webhook установлен

### Ошибка импорта модулей
```powershell
# Убедитесь, что виртуальное окружение активировано
.\venv\Scripts\Activate.ps1

# Переустановите зависимости
pip install -r requirements.txt
```

## Режимы работы

### Webhook режим (рекомендуется для production)
- Telegram отправляет сообщения на ваш сервер
- Требуется публичный HTTPS URL
- Более эффективен для высоких нагрузок
- Настройка: `MAX_MODE=webhook`

### Polling режим (для разработки)
- Приложение опрашивает MAX API каждые 30-60 секунд
- Не требует публичного URL
- Подходит для локального тестирования
- Настройка: `MAX_MODE=polling`

## Логи

Все операции логируются в консоль. Уровни логирования:
- `DEBUG` - подробная информация (для отладки)
- `INFO` - стандартная информация о работе
- `WARNING` - предупреждения
- `ERROR` - ошибки

Изменить уровень можно в `.env`:
```env
LOG_LEVEL=debug  # для подробных логов
```

## Дополнительные ресурсы

- [Документация MAX API](https://dev.max.ru/docs-api)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [MAX_API_INTEGRATION.md](./MAX_API_INTEGRATION.md) - подробная документация по интеграции
- [REFACTORING.md](./REFACTORING.md) - описание рефакторинга

## Следующие шаги

После успешного тестирования:

1. **Для production**: настройте webhook с HTTPS
2. **Масштабирование**: используйте несколько workers
3. **Мониторинг**: настройте логирование в файл
4. **Docker**: используйте Docker для развертывания
5. **CI/CD**: настройте автоматическое развертывание

## Контакты

Если возникли вопросы или проблемы:
- Проверьте документацию в репозитории
- Изучите логи приложения
- Проверьте статус API: http://localhost:8000/health
