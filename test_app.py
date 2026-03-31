"""
Скрипт для тестирования telegram-max-proxy в demo режиме
"""
import asyncio
import httpx
import json
from datetime import datetime
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


async def test_api_endpoints():
    """Тестирование API endpoints приложения"""
    base_url = "http://127.0.0.1:8000"
    
    print("=" * 60)
    print("Тестирование telegram-max-proxy")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {base_url}")
    print("=" * 60)
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        
        # Тест 1: Root endpoint
        print("[TEST 1] Root endpoint (GET /)")
        try:
            response = await client.get(f"{base_url}/")
            print(f"   [OK] Статус: {response.status_code}")
            data = response.json()
            print(f"   Ответ: {json.dumps(data, indent=6, ensure_ascii=False)}")
        except Exception as e:
            print(f"   [ERROR] Ошибка: {e}")
        print()
        
        # Тест 2: Health check
        print("[TEST 2] Health check (GET /health)")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   [OK] Статус: {response.status_code}")
            data = response.json()
            print(f"   Ответ: {json.dumps(data, indent=6, ensure_ascii=False)}")
        except Exception as e:
            print(f"   [ERROR] Ошибка: {e}")
        print()
        
        # Тест 3: Bot info
        print("[TEST 3] Bot info (GET /bot/info)")
        try:
            response = await client.get(f"{base_url}/bot/info")
            print(f"   [OK] Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Ответ: {json.dumps(data, indent=6, ensure_ascii=False)}")
            else:
                print(f"   [WARN] Ответ: {response.text}")
        except Exception as e:
            print(f"   [ERROR] Ошибка: {e}")
        print()
        
        # Тест 4: Telegram webhook endpoint (POST)
        print("[TEST 4] Telegram webhook (POST /webhook/telegram)")
        test_update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser"
                },
                "chat": {
                    "id": 123456789,
                    "type": "private",
                    "username": "testuser"
                },
                "date": 1234567890,
                "text": "Hello from test!"
            }
        }
        try:
            response = await client.post(
                f"{base_url}/webhook/telegram",
                json=test_update
            )
            print(f"   [OK] Статус: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Ответ: {json.dumps(data, indent=6, ensure_ascii=False)}")
            else:
                print(f"   [WARN] Ответ: {response.text}")
        except Exception as e:
            print(f"   [ERROR] Ошибка: {e}")
        print()
        
        # Тест 5: OpenAPI docs
        print("[TEST 5] OpenAPI документация (GET /docs)")
        try:
            response = await client.get(f"{base_url}/docs")
            print(f"   [OK] Статус: {response.status_code}")
            if response.status_code == 200:
                print(f"   Документация доступна по адресу: {base_url}/docs")
        except Exception as e:
            print(f"   [ERROR] Ошибка: {e}")
        print()
    
    print("=" * 60)
    print("[SUCCESS] Тестирование завершено!")
    print("=" * 60)


if __name__ == "__main__":
    print("\nОжидание запуска сервера...\n")
    asyncio.run(test_api_endpoints())
