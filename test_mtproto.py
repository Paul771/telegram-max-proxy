import asyncio
import sys
from config import settings
from adapters.telegram import TelegramClient
from utils.proxy_helper import create_proxy_url, validate_mtproto_secret
from utils.logger import setup_logger

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = setup_logger(__name__, "debug")

async def test_mtproto():
    """Тест подключения к Telegram через MTProto прокси"""
    
    print("=" * 60)
    print("ТЕСТ MTPROTO ПРОКСИ ДЛЯ TELEGRAM")
    print("=" * 60)
    print()
    
    # Проверка настроек MTProto
    if settings.mtproto_proxy_host and settings.mtproto_proxy_port and settings.mtproto_proxy_secret:
        print("[INFO] MTProto прокси настроен:")
        print(f"  Host: {settings.mtproto_proxy_host}")
        print(f"  Port: {settings.mtproto_proxy_port}")
        print(f"  Secret: {settings.mtproto_proxy_secret[:20]}...")
        print()
        
        # Валидация секрета
        print("1. Проверка валидности секрета...")
        if validate_mtproto_secret(settings.mtproto_proxy_secret):
            print("   [OK] Секрет валиден")
        else:
            print("   [ERROR] Секрет невалиден!")
            print("   Секрет должен:")
            print("   - Быть в hex формате")
            print("   - Иметь минимум 32 символа")
            print("   - Начинаться с 'dd' или 'ee'")
            return
    else:
        print("[WARNING] MTProto прокси не настроен!")
        print()
        print("Для настройки добавьте в .env файл:")
        print("  MTPROTO_PROXY_HOST=proxy.example.com")
        print("  MTPROTO_PROXY_PORT=443")
        print("  MTPROTO_PROXY_SECRET=dd1234567890abcdef...")
        print()
        print("Получите MTProto прокси:")
        print("  - https://t.me/proxy")
        print("  - https://mtproto.co")
        print("  - @MTProxybot в Telegram")
        return
    
    print()
    print("2. Создание прокси URL...")
    proxy_url = create_proxy_url(
        http_proxy=settings.http_proxy,
        socks_proxy=settings.socks_proxy,
        mtproto_host=settings.mtproto_proxy_host,
        mtproto_port=settings.mtproto_proxy_port,
        mtproto_secret=settings.mtproto_proxy_secret
    )
    
    if proxy_url:
        print(f"   [OK] Proxy URL: {proxy_url}")
    else:
        print("   [ERROR] Не удалось создать proxy URL")
        return
    
    print()
    print("3. Подключение к Telegram Bot API...")
    print(f"   Bot Token: {settings.telegram_bot_token[:20]}...")
    
    # Создание клиента с прокси
    telegram_client = TelegramClient(
        bot_token=settings.telegram_bot_token,
        proxy_url=proxy_url
    )
    
    try:
        bot_info = await telegram_client.get_me()
        
        print("   [OK] Подключение успешно!")
        print(f"   Bot ID: {bot_info.get('id')}")
        print(f"   Bot Username: @{bot_info.get('username')}")
        print(f"   Bot Name: {bot_info.get('first_name')}")
        print()
        
        print("4. Получение последних обновлений...")
        updates = await telegram_client.get_updates(limit=10)
        print(f"   [OK] Получено обновлений: {len(updates)}")
        
        if updates:
            print()
            print("   Последние сообщения:")
            for i, update in enumerate(updates[-5:], 1):
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg.get('chat', {}).get('id')
                    text = msg.get('text', '[нет текста]')
                    date = msg.get('date')
                    from datetime import datetime
                    dt = datetime.fromtimestamp(date)
                    print(f"   {i}. [{dt.strftime('%Y-%m-%d %H:%M:%S')}] Chat: {chat_id}")
                    print(f"      Текст: {text[:80]}")
        
        print()
        print("=" * 60)
        print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 60)
        print()
        print("Теперь вы можете запустить основной сервис:")
        print("  python main.py")
        
    except Exception as e:
        print(f"   [ERROR] Ошибка подключения: {type(e).__name__}")
        print(f"   Детали: {str(e)[:300]}")
        print()
        print("=" * 60)
        print("[FAILED] ТЕСТ НЕ ПРОЙДЕН")
        print("=" * 60)
        print()
        print("РЕКОМЕНДАЦИИ:")
        print("1. Проверьте, что MTProto прокси работает")
        print("2. Попробуйте другой публичный прокси")
        print("3. Проверьте правильность секрета")
        print("4. Убедитесь, что порт не заблокирован")
    
    finally:
        await telegram_client.close()

if __name__ == "__main__":
    asyncio.run(test_mtproto())
