# Как получить API ID и API Hash для Telethon

## Зачем это нужно?

Для использования вашего MTProto прокси через Telethon необходимы API credentials от Telegram.

**Ваш MTProto прокси:**
```
Host: pro.alotaxi.info
Port: 4515
Secret: eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d
```

Этот прокси будет работать только после получения API ID и API Hash.

## Пошаговая инструкция

### Шаг 1: Перейдите на my.telegram.org

Откройте в браузере: https://my.telegram.org

### Шаг 2: Войдите с номером телефона

1. Введите ваш номер телефона (тот же, что привязан к Telegram)
2. Нажмите "Next"
3. Вы получите код подтверждения в Telegram
4. Введите код

### Шаг 3: Перейдите в API development tools

После входа:
1. Нажмите "API development tools"
2. Если это первый раз, заполните форму:
   - **App title**: telegram-max-proxy (или любое название)
   - **Short name**: tmproxy (или любое короткое имя)
   - **Platform**: Other
   - **Description**: Telegram to MAX proxy (необязательно)

### Шаг 4: Получите credentials

После создания приложения вы увидите:

```
App api_id: 12345678
App api_hash: 0123456789abcdef0123456789abcdef
```

**ВАЖНО:** Сохраните эти значения! Они понадобятся для настройки.

### Шаг 5: Добавьте в .env

Откройте файл `.env` и добавьте:

```env
# Режим Telethon для MTProto
TELEGRAM_MODE=telethon

# API credentials от my.telegram.org
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=0123456789abcdef0123456789abcdef

# Ваш MTProto прокси (уже настроен)
MTPROTO_PROXY_HOST=pro.alotaxi.info
MTPROTO_PROXY_PORT=4515
MTPROTO_PROXY_SECRET=eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d
```

### Шаг 6: Тестирование

```bash
cd telegram-max-proxy
.\venv\Scripts\activate
python test_telethon.py
```

Если все настроено правильно, вы увидите:
```
[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
```

И получите **session string** - сохраните его в .env:
```env
TELEGRAM_SESSION_STRING=полученная_строка
```

### Шаг 7: Запуск

```bash
python main.py
```

## Полная конфигурация .env

```env
# ============================================
# TELETHON РЕЖИМ С MTPROTO
# ============================================

# Режим работы
TELEGRAM_MODE=telethon

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90

# API credentials (получить на https://my.telegram.org)
TELEGRAM_API_ID=ваш_api_id
TELEGRAM_API_HASH=ваш_api_hash

# Session string (получите при первом запуске)
# TELEGRAM_SESSION_STRING=

# MTProto прокси
MTPROTO_PROXY_HOST=pro.alotaxi.info
MTPROTO_PROXY_PORT=4515
MTPROTO_PROXY_SECRET=eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d

# MAX API
MAX_API_BASE_URL=https://platform-api.max.ru
MAX_API_TOKEN=f9LHodD0cOLKLgwc04S_ZL_CV6vPKCYR7tE956kl_XOUySym7n65pAdre7pSAEVV53PWLwcpRlptEnNanPHy
MAX_TIMEOUT=30
MAX_MODE=webhook

# Маппинг чатов
CHAT_USER_MAPPING={"-1001461615203": "default_max_user"}

# Сервер
HOST=127.0.0.1
PORT=8000
LOG_LEVEL=debug
```

## Часто задаваемые вопросы

### Q: Зачем нужны API ID и API Hash?

A: Telethon использует нативный MTProto протокол Telegram, который требует регистрации приложения. Это стандартное требование Telegram для всех приложений, использующих MTProto.

### Q: Это безопасно?

A: Да, это официальный способ работы с Telegram API. API credentials привязаны к вашему аккаунту и используются только для аутентификации вашего приложения.

### Q: Можно ли использовать без API credentials?

A: Нет, для MTProto прокси через Telethon они обязательны. Альтернатива - использовать обычный SOCKS5/HTTP прокси в режиме bot_api.

### Q: Что делать, если забыл API credentials?

A: Просто зайдите снова на https://my.telegram.org - ваши credentials будут там отображаться.

## Поддержка

Если возникли проблемы:
1. Проверьте, что вы вошли на my.telegram.org с правильным номером
2. Убедитесь, что скопировали API ID и API Hash полностью
3. Проверьте, что в .env нет лишних пробелов или кавычек
4. См. документацию: `TELETHON_GUIDE.md`

---

**После получения API credentials ваш MTProto прокси заработает!**
