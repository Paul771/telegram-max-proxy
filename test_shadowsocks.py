import asyncio
import httpx
import sys

async def test_shadowsocks():
    """Тест Shadowsocks SOCKS5 прокси"""
    
    print("=" * 60)
    print("ТЕСТ SHADOWSOCKS SOCKS5 ПРОКСИ")
    print("=" * 60)
    print()
    
    proxy_url = "socks5://127.0.0.1:1080"
    bot_token = "1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90"
    
    print(f"Прокси: {proxy_url}")
    print(f"Bot Token: {bot_token[:20]}...")
    print()
    
    try:
        print("1. Создание HTTP клиента с SOCKS5 прокси...")
        client = httpx.AsyncClient(
            proxy=proxy_url,
            timeout=30.0
        )
        print("   [OK] Клиент создан")
        
        print()
        print("2. Попытка подключения к Telegram API...")
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        response = await client.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        print("   [OK] Подключение успешно!")
        print()
        print("Информация о боте:")
        print(f"   Bot ID: {data['result']['id']}")
        print(f"   Bot Username: @{data['result']['username']}")
        print(f"   Bot Name: {data['result']['first_name']}")
        
        print()
        print("3. Получение обновлений...")
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates?limit=5"
        response = await client.get(url)
        response.raise_for_status()
        
        updates = response.json()
        print(f"   [OK] Получено обновлений: {len(updates['result'])}")
        
        if updates['result']:
            print()
            print("   Последние сообщения:")
            for i, update in enumerate(updates['result'][-3:], 1):
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg.get('chat', {}).get('id')
                    text = msg.get('text', '[нет текста]')
                    print(f"   {i}. Chat: {chat_id}, Text: {text[:50]}")
        
        await client.aclose()
        
        print()
        print("=" * 60)
        print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("=" * 60)
        print()
        print("Shadowsocks прокси работает отлично!")
        print("Теперь можно запустить основной сервис:")
        print("  python main.py")
        
    except httpx.ConnectTimeout as e:
        print(f"   [ERROR] Таймаут подключения")
        print(f"   Детали: {e}")
        print()
        print("ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Shadowsocks не запущен или не работает")
        print("2. Порт 1080 неправильный (проверьте настройки Shadowsocks)")
        print("3. Shadowsocks не настроен для локального прокси")
        
    except httpx.ProxyError as e:
        print(f"   [ERROR] Ошибка прокси")
        print(f"   Детали: {e}")
        print()
        print("ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("1. Shadowsocks не поддерживает SOCKS5")
        print("2. Неправильные настройки прокси")
        
    except Exception as e:
        print(f"   [ERROR] Ошибка: {type(e).__name__}")
        print(f"   Детали: {str(e)[:200]}")
        print()
        print("Проверьте настройки Shadowsocks")

if __name__ == "__main__":
    asyncio.run(test_shadowsocks())
