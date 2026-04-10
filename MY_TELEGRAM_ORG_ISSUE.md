# ВАЖНО: Проблема с my.telegram.org

## Текущая ситуация

При попытке создать приложение на https://my.telegram.org возникает ошибка `[Object Object]` или `[Error]` при заполнении поля URL.

**Дата проблемы:** 2026-04-10

## Альтернативные решения

### Решение 1: Подождите и попробуйте позже

Возможно, это временная проблема с сайтом my.telegram.org. Попробуйте:
- Через несколько часов
- В другое время суток
- На следующий день

### Решение 2: Используйте проект БЕЗ Telethon (режим bot_api)

Проект полностью работает в режиме **bot_api** с обычными прокси.

#### Вариант A: С VPN/SOCKS5 прокси

Если у вас есть VPN клиент с SOCKS5:

**Популярные VPN и их SOCKS5 порты:**
- **Shadowsocks**: `socks5://127.0.0.1:1080`
- **V2Ray**: `socks5://127.0.0.1:10808`
- **Clash**: `socks5://127.0.0.1:7891`
- **Другие**: проверьте настройки вашего VPN

**Настройка .env:**
```env
# Режим Bot API (по умолчанию)
TELEGRAM_MODE=bot_api

# SOCKS5 прокси от VPN
SOCKS_PROXY=socks5://127.0.0.1:1080

# Остальные настройки
TELEGRAM_BOT_TOKEN=1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90
MAX_API_TOKEN=f9LHodD0cOLKLgwc04S_ZL_CV6vPKCYR7tE956kl_XOUySym7n65pAdre7pSAEVV53PWLwcpRlptEnNanPHy
CHAT_USER_MAPPING={"-1001461615203": "default_max_user"}
```

**Как узнать порт SOCKS5 вашего VPN:**
1. Откройте настройки VPN клиента
2. Найдите раздел "Local SOCKS5" или "Proxy Settings"
3. Скопируйте адрес и порт (обычно 127.0.0.1:порт)

#### Вариант B: Развернуть на VPS за границей

Самое надежное решение - развернуть проект на сервере с прямым доступом к Telegram:

**Рекомендуемые провайдеры:**
- DigitalOcean (от $4/месяц)
- Hetzner (от €4/месяц)
- Linode (от $5/месяц)
- Vultr (от $2.5/месяц)

**Преимущества:**
- ✅ Не нужен прокси
- ✅ Стабильное подключение 24/7
- ✅ Высокая скорость
- ✅ Не зависит от локальных блокировок

**Быстрая настройка на VPS:**
```bash
# 1. Подключитесь к VPS
ssh root@your-server-ip

# 2. Установите зависимости
apt update
apt install python3 python3-pip python3-venv git -y

# 3. Клонируйте проект
git clone https://github.com/Paul771/telegram-max-proxy.git
cd telegram-max-proxy

# 4. Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 5. Установите зависимости
pip install -r requirements.txt

# 6. Настройте .env (без прокси!)
nano .env
# Укажите токены, БЕЗ прокси настроек

# 7. Запустите
python main.py
```

### Решение 3: Попробуйте через Telegram Desktop

Иногда API credentials можно получить через десктопное приложение:

1. Установите **Telegram Desktop** (не Web версию)
2. Войдите в аккаунт
3. Попробуйте открыть https://my.telegram.org в браузере после входа в Desktop
4. Или поищите в настройках Desktop опцию "Developer Tools"

### Решение 4: Обратитесь в поддержку Telegram

Если проблема сохраняется:

1. Напишите в **@BotSupport** в Telegram
2. Опишите проблему с my.telegram.org
3. Попросите помочь получить API credentials
4. Или спросите об альтернативных способах

### Решение 5: Используйте существующие API credentials (если есть)

Если вы ранее создавали приложение на my.telegram.org:
1. Зайдите на https://my.telegram.org
2. Ваши существующие API credentials должны отображаться
3. Скопируйте их и используйте

## Текущий статус проекта

**Проект полностью работоспособен в режиме bot_api!**

✅ Что работает:
- Bot API режим (по умолчанию)
- MAX API интеграция
- Поддержка HTTP/SOCKS5 прокси
- Все базовые функции

⏳ Что требует API credentials:
- Telethon режим с MTProto прокси

## Рекомендация

**Для немедленного запуска:**

1. **Если есть VPN с SOCKS5:**
   - Узнайте порт SOCKS5 (обычно 1080, 7891, 10808)
   - Добавьте в .env: `SOCKS_PROXY=socks5://127.0.0.1:порт`
   - Запустите: `python main.py`

2. **Если нет VPN:**
   - Разверните на VPS за границей
   - Или подождите, пока my.telegram.org заработает

3. **Для MTProto прокси:**
   - Дождитесь исправления my.telegram.org
   - Получите API credentials
   - Переключитесь на Telethon режим

## Проверка работы без Telethon

Вы можете протестировать проект прямо сейчас:

```bash
# 1. Убедитесь, что режим bot_api (по умолчанию)
# В .env должно быть: TELEGRAM_MODE=bot_api (или не указано)

# 2. Если есть VPN, добавьте SOCKS5
# SOCKS_PROXY=socks5://127.0.0.1:1080

# 3. Запустите тест MAX API
python check_max_messages.py

# 4. Если есть прокси, запустите проект
python main.py
```

---

**Проект готов к использованию! MTProto можно добавить позже, когда my.telegram.org заработает.**
