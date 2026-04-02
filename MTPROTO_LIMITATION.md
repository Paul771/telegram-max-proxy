# ВАЖНО: MTProto прокси и Telegram Bot API

## Проблема

**MTProto прокси НЕ работает с Telegram Bot API!**

MTProto прокси предназначен только для:
- Telegram клиентских приложений (мобильные, десктопные)
- Библиотек типа Telethon, Pyrogram (для User API)

Telegram Bot API использует обычный HTTPS протокол и требует:
- HTTP прокси
- SOCKS5 прокси
- VPN

## Результат тестирования вашего MTProto прокси

```
Host: pro.alotaxi.info
Port: 4515
Secret: eee9a4f23b1d768c04a8d7f39120ca5b...

Статус: Прокси доступен, но не работает для Bot API
Ошибка: Connection closed unexpectedly
```

## Альтернативные решения

### Решение 1: Использовать обычный SOCKS5/HTTP прокси

Вам нужен обычный SOCKS5 или HTTP прокси, а не MTProto.

**Где получить:**
- Публичные прокси: https://www.proxy-list.download/SOCKS5
- Платные прокси: https://proxy6.net, https://proxy-seller.ru
- VPN с SOCKS5: Shadowsocks, V2Ray, Clash

**Настройка в .env:**
```env
# Для SOCKS5
SOCKS_PROXY=socks5://proxy-host:port

# Для HTTP
HTTP_PROXY=http://proxy-host:port
```

### Решение 2: Использовать VPN

Запустите VPN на вашем компьютере:
- Shadowsocks (предоставляет локальный SOCKS5 на 127.0.0.1:1080)
- V2Ray (предоставляет локальный SOCKS5 на 127.0.0.1:10808)
- Clash (предоставляет локальный SOCKS5 на 127.0.0.1:7891)

Затем в .env:
```env
SOCKS_PROXY=socks5://127.0.0.1:1080
```

### Решение 3: Развернуть на VPS за границей

Самое надежное решение:

1. Арендуйте VPS (DigitalOcean, Linode, AWS, Hetzner)
2. Выберите локацию за пределами блокировки (Европа, США)
3. Установите проект на сервер
4. Запустите без прокси (прямой доступ к Telegram)

**Преимущества:**
- Стабильное подключение
- Высокая скорость
- Не нужен прокси
- Работает 24/7

### Решение 4: Использовать локальный Telegram Bot API сервер

Telegram предоставляет возможность запустить свой Bot API сервер, который может работать через MTProto прокси.

**Сложность:** Высокая
**Документация:** https://github.com/tdlib/telegram-bot-api

## Рекомендация

Для вашего случая рекомендую:

1. **Быстрое решение:** Установите Shadowsocks или V2Ray с SOCKS5 прокси
2. **Долгосрочное решение:** Разверните проект на VPS за границей

## Обновленная конфигурация .env

Удалите MTProto настройки и используйте SOCKS5/HTTP:

```env
# Production configuration
# Telegram Bot API
TELEGRAM_BOT_TOKEN=1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90
TELEGRAM_WEBHOOK_PATH=/webhook/telegram

# MAX Messenger API
MAX_API_BASE_URL=https://platform-api.max.ru
MAX_API_TOKEN=f9LHodD0cOLKLgwc04S_ZL_CV6vPKCYR7tE956kl_XOUySym7n65pAdre7pSAEVV53PWLwcpRlptEnNanPHy
MAX_TIMEOUT=30

# Режим работы с MAX API: webhook или polling
MAX_MODE=webhook

# Маппинг чатов (JSON формат)
CHAT_USER_MAPPING={"-1001461615203": "default_max_user"}

# Proxy settings
HOST=127.0.0.1
PORT=8000

# ИСПОЛЬЗУЙТЕ SOCKS5 или HTTP прокси (НЕ MTProto!)
# Пример с VPN:
# SOCKS_PROXY=socks5://127.0.0.1:1080

# Пример с публичным прокси:
# SOCKS_PROXY=socks5://proxy-host:port
# HTTP_PROXY=http://proxy-host:port

# Уровень логирования: debug, info, warning, error
LOG_LEVEL=debug
```

## Следующие шаги

1. Получите SOCKS5 или HTTP прокси (не MTProto!)
2. Обновите .env файл
3. Запустите тест: `python test_proxy.py`
4. Запустите сервис: `python main.py`
