import asyncio
import httpx
import sys
from config import settings
from adapters.telegram import TelegramClient
from adapters.max import MaxClient
from utils.logger import setup_logger

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

logger = setup_logger(__name__, "debug")

async def test_connections():
    """Тест подключения к Telegram и MAX API"""
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЙ")
    print("=" * 60)
    
    # Тест Telegram
    print("\n1. Проверка Telegram Bot API...")
    print(f"   Token: {settings.telegram_bot_token[:20]}...")
    
    telegram_client = TelegramClient(bot_token=settings.telegram_bot_token)
    
    try:
        bot_info = await telegram_client.get_me()
        print(f"   [OK] Подключение успешно!")
        print(f"   Bot ID: {bot_info.get('id')}")
        print(f"   Bot Username: @{bot_info.get('username')}")
        print(f"   Bot Name: {bot_info.get('first_name')}")
    except Exception as e:
        print(f"   [ERROR] Ошибка подключения: {type(e).__name__}")
        print(f"   Детали: {str(e)[:200]}")
    
    # Тест MAX API
    print("\n2. Проверка MAX API...")
    print(f"   Base URL: {settings.max_api_base_url}")
    print(f"   Token: {settings.max_api_token[:20]}...")
    
    max_client = MaxClient(
        api_token=settings.max_api_token,
        base_url=settings.max_api_base_url,
        timeout=settings.max_timeout
    )
    
    try:
        health = await max_client.health_check()
        if health:
            print(f"   [OK] MAX API доступен")
        else:
            print(f"   [ERROR] MAX API недоступен")
    except Exception as e:
        print(f"   [ERROR] Ошибка подключения: {type(e).__name__}")
        print(f"   Детали: {str(e)[:200]}")
    
    # Проверка маппинга
    print("\n3. Проверка маппинга чатов...")
    print(f"   Маппинг: {settings.chat_user_mapping}")
    
    # Получение обновлений от Telegram
    print("\n4. Получение последних обновлений от Telegram...")
    try:
        updates = await telegram_client.get_updates(limit=10)
        print(f"   Получено обновлений: {len(updates)}")
        
        if updates:
            print("\n   Последние сообщения:")
            for i, update in enumerate(updates[-5:], 1):
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg.get('chat', {}).get('id')
                    text = msg.get('text', '[нет текста]')
                    date = msg.get('date')
                    print(f"   {i}. Chat ID: {chat_id}, Date: {date}, Text: {text[:50]}")
    except Exception as e:
        print(f"   [ERROR] Ошибка получения обновлений: {type(e).__name__}")
    
    # Закрытие клиентов
    await telegram_client.close()
    await max_client.close()
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_connections())
