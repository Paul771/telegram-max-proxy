import asyncio
import socket
import sys

async def test_shadowsocks_detailed():
    """Детальная диагностика Shadowsocks прокси"""
    
    print("=" * 60)
    print("ДЕТАЛЬНАЯ ДИАГНОСТИКА SHADOWSOCKS")
    print("=" * 60)
    print()
    
    # Тест 1: Проверка порта
    print("1. Проверка доступности порта 1080...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        
        if result == 0:
            print("   [OK] Порт 1080 открыт и доступен")
        else:
            print(f"   [ERROR] Порт 1080 недоступен (код: {result})")
            return
    except Exception as e:
        print(f"   [ERROR] Ошибка проверки порта: {e}")
        return
    
    # Тест 2: Проверка типа прокси
    print()
    print("2. Проверка типа Shadowsocks прокси...")
    print("   Shadowsocks может работать в режимах:")
    print("   - HTTP прокси (обычно порт 1087)")
    print("   - SOCKS5 прокси (обычно порт 1080)")
    print()
    print("   Попробуем оба варианта...")
    
    # Тест 3: HTTP прокси
    print()
    print("3. Тест через HTTP прокси...")
    try:
        import httpx
        client = httpx.AsyncClient(
            proxy="http://127.0.0.1:1080",
            timeout=10.0
        )
        response = await client.get("https://api.telegram.org/bot1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90/getMe")
        data = response.json()
        print(f"   [OK] HTTP прокси работает!")
        print(f"   Bot: @{data['result']['username']}")
        await client.aclose()
        
        print()
        print("=" * 60)
        print("[SUCCESS] Shadowsocks работает как HTTP прокси!")
        print("=" * 60)
        print()
        print("Обновите .env:")
        print("HTTP_PROXY=http://127.0.0.1:1080")
        print("# SOCKS_PROXY=socks5://127.0.0.1:1080")
        return
        
    except Exception as e:
        print(f"   [FAILED] HTTP прокси не работает: {type(e).__name__}")
    
    # Тест 4: Проверка других портов
    print()
    print("4. Проверка других возможных портов Shadowsocks...")
    ports_to_check = [1087, 8388, 8080, 7890]
    
    for port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"   [INFO] Порт {port} открыт - попробуйте его")
        except:
            pass
    
    print()
    print("=" * 60)
    print("[INFO] РЕКОМЕНДАЦИИ")
    print("=" * 60)
    print()
    print("Shadowsocks может быть настроен по-разному:")
    print()
    print("1. Откройте настройки Shadowsocks")
    print("2. Найдите раздел 'Local Proxy' или 'Локальный прокси'")
    print("3. Проверьте:")
    print("   - Тип прокси (HTTP или SOCKS5)")
    print("   - Порт (обычно 1080 для SOCKS5, 1087 для HTTP)")
    print("   - Включен ли 'Allow connections from LAN'")
    print()
    print("4. Попробуйте в .env:")
    print("   HTTP_PROXY=http://127.0.0.1:1087")
    print("   или")
    print("   SOCKS_PROXY=socks5://127.0.0.1:1080")
    print()
    print("5. Или используйте 'System Proxy' режим в Shadowsocks")

if __name__ == "__main__":
    asyncio.run(test_shadowsocks_detailed())
