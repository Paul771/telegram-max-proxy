# Telethon Integration Guide - MTProto Support

## Обзор

Проект теперь поддерживает два режима работы с Telegram:

1. **Bot API** (стандартный) - через HTTPS API
2. **Telethon** (MTProto) - нативный протокол Telegram с поддержкой MTProto прокси

## Преимущества Telethon режима

- ✅ **Поддержка MTProto прокси** - работает с вашим MTProto прокси
- ✅ **Обход блокировок** - MTProto прокси специально разработан для обхода блокировок
- ✅ **Нативный протокол** - прямое подключение к серверам Telegram
- ✅ **Стабильность** - меньше зависимости от внешних API

## Быстрый старт

### Шаг 1: Получите API credentials

1. Перейдите на https://my.telegram.org
2. Войдите с вашим номером телефона
3. Перейдите в "API development tools"
4. Создайте приложение и получите:
   - **API ID** (число)
   - **API Hash** (строка)

### Шаг 2: Настройте .env

Добавьте в `.env` файл:

```env
# Режим работы Telegram
TELEGRAM_MODE=telethon

# Telethon credentials (получить на https://my.telegram.org)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef

# MTProto прокси (ваш существующий)
MTPROTO_PROXY_HOST=pro.alotaxi.info
MTPROTO_PROXY_PORT=4515
MTPROTO_PROXY_SECRET=eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d

# Остальные настройки остаются без изменений
TELEGRAM_BOT_TOKEN=1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90
MAX_API_TOKEN=f9LHodD0cOLKLgwc04S_ZL_CV6vPKCYR7tE956kl_XOUySym7n65pAdre7pSAEVV53PWLwcpRlptEnNanPHy
CHAT_USER_MAPPING={"-1001461615203": "default_max_user"}
```

### Шаг 3: Тестирование

```bash
cd telegram-max-proxy
.\venv\Scripts\activate
python test_telethon.py
```

Если тест успешен, вы увидите:
```
[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
```

И получите **session string** - сохраните его в .env:
```env
TELEGRAM_SESSION_STRING=полученная_строка_сессии
```

### Шаг 4: Запуск

```bash
python main.py
```

## Сравнение режимов

| Функция | Bot API | Telethon |
|---------|---------|----------|
| HTTP/SOCKS5 прокси | ✅ | ❌ |
| MTProto прокси | ❌ | ✅ |
| Простота настройки | ✅ Легко | ⚠️ Требует API ID/Hash |
| Обход блокировок | ⚠️ Зависит от прокси | ✅ Отлично |
| Стабильность | ✅ Хорошо | ✅ Отлично |

## Полная конфигурация .env

```env
# ============================================
# РЕЖИМ 1: Bot API (стандартный)
# ============================================
# TELEGRAM_MODE=bot_api
# HTTP_PROXY=http://proxy:port
# или
# SOCKS_PROXY=socks5://proxy:port

# ============================================
# РЕЖИМ 2: Telethon (MTProto) - РЕКОМЕНДУЕТСЯ
# ============================================
TELEGRAM_MODE=telethon

# Telegram API credentials (https://my.telegram.org)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef

# Session string (получите при первом запуске)
# TELEGRAM_SESSION_STRING=

# MTProto прокси
MTPROTO_PROXY_HOST=pro.alotaxi.info
MTPROTO_PROXY_PORT=4515
MTPROTO_PROXY_SECRET=eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d

# ============================================
# ОБЩИЕ НАСТРОЙКИ
# ============================================
TELEGRAM_BOT_TOKEN=1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90
TELEGRAM_WEBHOOK_PATH=/webhook/telegram

MAX_API_BASE_URL=https://platform-api.max.ru
MAX_API_TOKEN=f9LHodD0cOLKLgwc04S_ZL_CV6vPKCYR7tE956kl_XOUySym7n65pAdre7pSAEVV53PWLwcpRlptEnNanPHy
MAX_TIMEOUT=30
MAX_MODE=webhook

CHAT_USER_MAPPING={"-1001461615203": "default_max_user"}

HOST=127.0.0.1
PORT=8000
LOG_LEVEL=debug
```

## Переключение между режимами

Просто измените `TELEGRAM_MODE` в .env:

```env
# Для Bot API с HTTP/SOCKS прокси
TELEGRAM_MODE=bot_api

# Для Telethon с MTProto прокси
TELEGRAM_MODE=telethon
```

## Устранение проблем

### Ошибка: "API ID and API Hash required"

Получите credentials на https://my.telegram.org и добавьте в .env:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
```

### Ошибка подключения к MTProto прокси

1. Проверьте доступность прокси:
```bash
Test-NetConnection -ComputerName pro.alotaxi.info -Port 4515
```

2. Проверьте правильность secret (должен быть в hex формате)

3. Попробуйте другой MTProto прокси

### Session string

При первом запуске Telethon создаст сессию и выведет session string.
Сохраните его в .env для переиспользования:

```env
TELEGRAM_SESSION_STRING=1AQAAA...полная_строка...
```

## Архитектура

```
main.py
  ↓
telegram_factory.py (выбор режима)
  ↓
  ├─→ telegram.py (Bot API + HTTP/SOCKS)
  └─→ telegram_telethon.py (Telethon + MTProto)
```

## API совместимость

Оба адаптера реализуют одинаковый интерфейс:
- `send_message(chat_id, text, ...)`
- `get_me()`
- `close()`

Код ProxyService работает с обоими режимами без изменений.

## Рекомендации

1. **Для продакшена**: используйте Telethon с MTProto прокси
2. **Для разработки**: можно использовать Bot API с VPN
3. **Сохраняйте session string**: это ускорит последующие запуски
4. **Мониторинг**: проверяйте логи на наличие ошибок подключения

## Дополнительная информация

- [Telethon документация](https://docs.telethon.dev/)
- [MTProto протокол](https://core.telegram.org/mtproto)
- [Telegram Bot API](https://core.telegram.org/bots/api)
