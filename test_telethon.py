import asyncio
import sys
from config import settings
from adapters.telegram_factory import create_telegram_client, prepare_mtproto_proxy
from utils.logger import setup_logger

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = setup_logger(__name__, "debug")

async def test_telethon():
    """Тест подключения через Telethon с MTProto прокси"""
    
    print("=" * 60)
    print("ТЕСТ TELETHON РЕЖИМА (MTProto)")
    print("=" * 60)
    print()
    
    # Проверка настроек
    print("1. Проверка конфигурации...")
    print(f"   Режим: {settings.telegram_mode}")
    print(f"   Bot Token: {settings.telegram_bot_token[:20]}...")
    
    if settings.telegram_mode != "telethon":
        print()
        print("[WARNING] Режим не установлен в 'telethon'")
        print("Установите в .env: TELEGRAM_MODE=telethon")
        return
    
    if not settings.telegram_api_id or not settings.telegram_api_hash:
        print()
        print("[ERROR] Не указаны API ID и API Hash")
        print("Получите их на https://my.telegram.org")
        print("Добавьте в .env:")
        print("  TELEGRAM_API_ID=your_api_id")
        print("  TELEGRAM_API_HASH=your_api_hash")
        return
    
    print(f"   API ID: {settings.telegram_api_id}")
    print(f"   API Hash: {settings.telegram_api_hash[:10]}...")
    
    # Проверка MTProto прокси
    mtproto_proxy = None
    if settings.mtproto_proxy_host and settings.mtproto_proxy_port and settings.mtproto_proxy_secret:
        print()
        print("2. MTProto прокси настроен:")
        print(f"   Host: {settings.mtproto_proxy_host}")
        print(f"   Port: {settings.mtproto_proxy_port}")
        print(f"   Secret: {settings.mtproto_proxy_secret[:20]}...")
        
        mtproto_proxy = prepare_mtproto_proxy(
            host=settings.mtproto_proxy_host,
            port=settings.mtproto_proxy_port,
            secret=settings.mtproto_proxy_secret
        )
    else:
        print()
        print("2. MTProto прокси не настроен")
        print("   Будет использовано прямое подключение")
    
    print()
    print("3. Создание Telethon клиента...")
    
    try:
        client = create_telegram_client(
            mode="telethon",
            bot_token=settings.telegram_bot_token,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
            session_string=settings.telegram_session_string,
            mtproto_proxy=mtproto_proxy
        )
        
        print("   [OK] Клиент создан")
        
        print()
        print("4. Запуск и авторизация...")
        session_string = await client.start()
        
        print("   [OK] Авторизация успешна!")
        
        if not settings.telegram_session_string:
            print()
            print("   [INFO] Сохраните эту строку сессии в .env:")
            print(f"   TELEGRAM_SESSION_STRING={session_string}")
        
        print()
        print("5. Получение информации о боте...")
        bot_info = await client.get_me()
        
        print(f"   [OK] Bot ID: {bot_info.get('id')}")
        print(f"   [OK] Bot Username: @{bot_info.get('username')}")
        print(f"   [OK] Bot Name: {bot_info.get('first_name')}")
        
        print()
        print("6. Тест отправки сообщения...")
        print("   (пропущен - требуется chat_id)")
        
        print()
        print("=" * 60)
        print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 60)
        print()
        print("Telethon успешно подключен через MTProto!")
        print("Теперь вы можете запустить основной сервис:")
        print("  python main.py")
        
        # Остановка клиента
        await client.stop()
        
    except Exception as e:
        print(f"   [ERROR] Ошибка: {type(e).__name__}")
        print(f"   Детали: {str(e)[:300]}")
        print()
        print("=" * 60)
        print("[FAILED] ТЕСТ НЕ ПРОЙДЕН")
        print("=" * 60)
        print()
        print("РЕКОМЕНДАЦИИ:")
        print("1. Проверьте правильность API ID и API Hash")
        print("2. Проверьте настройки MTProto прокси")
        print("3. Убедитесь, что прокси работает")

if __name__ == "__main__":
    asyncio.run(test_telethon())
