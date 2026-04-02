# Настройка MTProto прокси для telegram-max-proxy

## Что такое MTProto прокси?

MTProto прокси - это специальный протокол прокси, разработанный Telegram для обхода блокировок. Он обеспечивает:
- Высокую скорость соединения
- Надежное шифрование
- Обфускацию трафика (выглядит как обычный HTTPS)
- Устойчивость к блокировкам

## Получение MTProto прокси

### Вариант 1: Публичные прокси

Найдите публичные MTProto прокси в Telegram:
- Канал @MTProxybot
- Канал @proxy
- Сайт https://mtproto.co
- Сайт https://mtpro.xyz

### Вариант 2: Свой прокси-сервер

Установите MTProto прокси на свой VPS:

```bash
# Клонируйте репозиторий
git clone https://github.com/TelegramMessenger/MTProxy
cd MTProxy

# Соберите прокси
make

# Получите секрет
head -c 16 /dev/urandom | xxd -ps

# Запустите прокси
./mtproto-proxy -u nobody -p 8888 -H 443 -S <your-secret> --aes-pwd proxy-secret proxy-multi.conf
```

## Формат MTProto прокси

MTProto прокси имеет следующие параметры:

1. **Host** - IP адрес или домен прокси-сервера
2. **Port** - Порт (обычно 443 или 8443)
3. **Secret** - Секретный ключ в hex формате

### Типы секретов:

- **dd-secret** (обфусцированный) - начинается с `dd`, маскирует трафик под HTTPS
- **ee-secret** (secure) - начинается с `ee`, дополнительное шифрование

Пример секрета: `dd1234567890abcdef1234567890abcdef`

## Настройка в проекте

### 1. Добавьте параметры в .env файл

```env
# MTProto Proxy настройки
MTPROTO_PROXY_HOST=proxy.example.com
MTPROTO_PROXY_PORT=443
MTPROTO_PROXY_SECRET=dd1234567890abcdef1234567890abcdef
```

### 2. Пример с реальными данными

Если вы получили ссылку вида:
```
tg://proxy?server=149.154.167.99&port=443&secret=dd00000000000000000000000000000000example.com
```

Извлеките параметры:
```env
MTPROTO_PROXY_HOST=149.154.167.99
MTPROTO_PROXY_PORT=443
MTPROTO_PROXY_SECRET=dd00000000000000000000000000000000example.com
```

### 3. Установите зависимости

```bash
cd telegram-max-proxy
.\venv\Scripts\activate
pip install httpx[socks]
```

### 4. Проверьте подключение

Создайте тестовый скрипт `test_mtproto.py`:

```python
import asyncio
from config import settings
from adapters.telegram import TelegramClient
from utils.proxy_helper import create_proxy_url, validate_mtproto_secret

async def test():
    # Проверка секрета
    if settings.mtproto_proxy_secret:
        if validate_mtproto_secret(settings.mtproto_proxy_secret):
            print("✓ MTProto secret is valid")
        else:
            print("✗ MTProto secret is invalid")
    
    # Создание прокси URL
    proxy_url = create_proxy_url(
        mtproto_host=settings.mtproto_proxy_host,
        mtproto_port=settings.mtproto_proxy_port,
        mtproto_secret=settings.mtproto_proxy_secret
    )
    
    print(f"Proxy URL: {proxy_url}")
    
    # Тест подключения
    client = TelegramClient(
        bot_token=settings.telegram_bot_token,
        proxy_url=proxy_url
    )
    
    try:
        bot_info = await client.get_me()
        print(f"✓ Connected! Bot: @{bot_info.get('username')}")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
    finally:
        await client.close()

asyncio.run(test())
```

Запустите тест:
```bash
python test_mtproto.py
```

## Приоритет прокси

Проект поддерживает несколько типов прокси одновременно. Приоритет:

1. **MTProto** (если все параметры указаны)
2. **SOCKS5** (если указан SOCKS_PROXY)
3. **HTTP** (если указан HTTP_PROXY)

Рекомендуется использовать MTProto как наиболее надежный вариант.

## Запуск сервиса

После настройки MTProto прокси запустите сервис:

```bash
python main.py
```

Проверьте статус:
```bash
curl http://127.0.0.1:8000/health
```

Должен вернуть:
```json
{
  "status": "healthy",
  "telegram_api": "connected",
  "max_api": "connected"
}
```

## Устранение проблем

### Ошибка: Invalid MTProto secret

Проверьте:
- Секрет должен быть в hex формате
- Минимальная длина 32 символа
- Должен начинаться с `dd` или `ee`

### Ошибка: Connection timeout

Проверьте:
- Прокси-сервер работает
- Порт открыт
- Нет блокировки файрволом
- Попробуйте другой публичный прокси

### MTProto прокси не работает

Попробуйте:
1. Проверить прокси в официальном Telegram клиенте
2. Использовать другой публичный прокси
3. Установить свой MTProto прокси на VPS

## Полезные ссылки

- [MTProxy GitHub](https://github.com/TelegramMessenger/MTProxy)
- [Список публичных прокси](https://t.me/proxy)
- [MTProto документация](https://core.telegram.org/mtproto)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## Безопасность

⚠️ **Важно:**
- Не используйте ненадежные публичные прокси для важных данных
- Публичные прокси могут логировать трафик
- Для продакшена рекомендуется свой MTProto прокси
- Регулярно меняйте прокси-серверы
