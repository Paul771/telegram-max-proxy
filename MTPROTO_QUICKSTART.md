# БЫСТРЫЙ СТАРТ: Настройка MTProto прокси

## Шаг 1: Получите данные MTProto прокси

У вас должны быть:
- **Host** (IP или домен)
- **Port** (обычно 443 или 8443)
- **Secret** (hex строка, начинается с dd или ee)

## Шаг 2: Добавьте в .env файл

Откройте файл `.env` и добавьте/раскомментируйте строки:

```env
MTPROTO_PROXY_HOST=ваш_хост
MTPROTO_PROXY_PORT=443
MTPROTO_PROXY_SECRET=ваш_секрет
```

**Пример:**
```env
MTPROTO_PROXY_HOST=149.154.167.99
MTPROTO_PROXY_PORT=443
MTPROTO_PROXY_SECRET=dd1234567890abcdef1234567890abcdef
```

## Шаг 3: Установите зависимости

```bash
cd telegram-max-proxy
.\venv\Scripts\activate
pip install httpx[socks]
```

## Шаг 4: Протестируйте подключение

```bash
python test_mtproto.py
```

Если тест успешен, вы увидите:
```
[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!
```

## Шаг 5: Запустите сервис

```bash
python main.py
```

## Проверка работы

Откройте новое окно терминала и выполните:

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

## Если что-то не работает

1. Проверьте правильность данных прокси
2. Попробуйте другой MTProto прокси
3. Убедитесь, что секрет в правильном формате (hex, начинается с dd/ee)
4. Проверьте логи сервиса на наличие ошибок

## Где взять MTProto прокси

- Telegram канал: https://t.me/proxy
- Бот: @MTProxybot
- Сайт: https://mtproto.co
- Сайт: https://mtpro.xyz

Подробная документация: см. файл `MTPROTO_SETUP.md`
