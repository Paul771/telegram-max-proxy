import asyncio
import sys
from config import settings
from adapters.telegram import TelegramClient
from utils.logger import setup_logger

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = setup_logger(__name__, "debug")

async def test_proxy():
    """Тест подключения к Telegram через прокси"""
    
    print("=" * 60)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К TELEGRAM API ЧЕРЕЗ ПРОКСИ")
    print("=" * 60)
    print()
    
    # Проверка настроек прокси
    proxy_url = settings.socks_proxy or settings.http_proxy
    
    if proxy_url:
        print(f"[INFO] Используется прокси: {proxy_url}")
    else:
        print("[WARNING] Прокси не настроен!")
        print("Для настройки прокси добавьте в .env файл:")
        print("  HTTP_PROXY=http://your-proxy:port")
        print("  или")
        print("  SOCKS_PROXY=socks5://your-proxy:port")
        print()
    
    print(f"Telegram Bot Token: {settings.telegram_bot_token[:20]}...")
    print()
    
    # Создание клиента с прокси
    telegram_client = TelegramClient(
        bot_token=settings.telegram_bot_token,
        proxy_url=proxy_url
    )
    
    try:
        print("1. Попытка подключения к Telegram Bot API...")
        bot_info = await telegram_client.get_me()
        
        print("[OK] Подключение успешно!")
        print(f"   Bot ID: {bot_info.get('id')}")
        print(f"   Bot Username: @{bot_info.get('username')}")
        print(f"   Bot Name: {bot_info.get('first_name')}")
        print()
        
        print("2. Получение последних обновлений...")
        updates = await telegram_client.get_updates(limit=10)
        print(f"[OK] Получено обновлений: {len(updates)}")
        
        if updates:
            print()
            print("Последние сообщения:")
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
        
    except Exception as e:
        print(f"[ERROR] Ошибка подключения: {type(e).__name__}")
        print(f"Детали: {str(e)[:300]}")
        print()
        print("=" * 60)
        print("[FAILED] ТЕСТ НЕ ПРОЙДЕН")
        print("=" * 60)
        print()
        print("РЕКОМЕНДАЦИИ:")
        if not proxy_url:
            print("1. Настройте прокси в .env файле")
            print("2. Используйте VPN для доступа к Telegram API")
        else:
            print("1. Проверьте правильность настроек прокси")
            print("2. Убедитесь, что прокси-сервер работает")
            print("3. Проверьте формат URL прокси:")
            print("   - HTTP: http://host:port")
            print("   - SOCKS5: socks5://host:port")
    
    finally:
        await telegram_client.close()

if __name__ == "__main__":
    asyncio.run(test_proxy())
