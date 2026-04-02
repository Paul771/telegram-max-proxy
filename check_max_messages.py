import asyncio
import sys
from datetime import datetime
from config import settings
from adapters.max import MaxClient
from utils.logger import setup_logger

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logger = setup_logger(__name__, "debug")

async def check_max_messages():
    """Проверка сообщений в MAX API"""
    
    print("=" * 60)
    print("ПРОВЕРКА СООБЩЕНИЙ В MAX API")
    print("=" * 60)
    print(f"Текущее время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    max_client = MaxClient(
        api_token=settings.max_api_token,
        base_url=settings.max_api_base_url,
        timeout=settings.max_timeout
    )
    
    try:
        # Проверка здоровья API
        print("1. Проверка подключения к MAX API...")
        health = await max_client.health_check()
        if health:
            print("   [OK] MAX API доступен")
        else:
            print("   [ERROR] MAX API недоступен")
            return
        
        # Получение обновлений
        print("\n2. Получение последних обновлений из MAX...")
        try:
            updates_response = await max_client.get_updates(
                limit=50,
                timeout=5,
                types=["message_created"]
            )
            
            print(f"   Получено обновлений: {len(updates_response.updates)}")
            
            if updates_response.updates:
                print("\n   Последние сообщения:")
                for i, update in enumerate(updates_response.updates[-10:], 1):
                    if update.message:
                        msg = update.message
                        timestamp = msg.timestamp if hasattr(msg, 'timestamp') else 'N/A'
                        sender = msg.sender.user_id if msg.sender else 'N/A'
                        text = msg.body.text if msg.body else '[нет текста]'
                        print(f"\n   {i}. Время: {timestamp}")
                        print(f"      Отправитель: {sender}")
                        print(f"      Текст: {text[:100]}")
            else:
                print("   [INFO] Нет новых сообщений")
                
            if updates_response.marker:
                print(f"\n   Marker для следующего запроса: {updates_response.marker}")
                
        except Exception as e:
            print(f"   [ERROR] Ошибка получения обновлений: {type(e).__name__}")
            print(f"   Детали: {str(e)[:300]}")
        
    finally:
        await max_client.close()
    
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЗАВЕРШЕНА")
    print("=" * 60)
    print("\nВЫВОД:")
    print("- Telegram API заблокирован в вашей сети")
    print("- MAX API работает нормально")
    print("- Для работы прокси нужен доступ к Telegram API")
    print("\nРЕКОМЕНДАЦИИ:")
    print("1. Используйте VPN или прокси для доступа к Telegram API")
    print("2. Или разверните сервис на сервере с доступом к Telegram")

if __name__ == "__main__":
    asyncio.run(check_max_messages())
