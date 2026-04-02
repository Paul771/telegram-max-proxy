import asyncio
import sys
from python_socks.async_.asyncio import Proxy
from python_socks import ProxyType

async def test_mtproto_as_socks():
    """Тест MTProto прокси как SOCKS5"""
    
    print("=" * 60)
    print("ТЕСТ MTPROTO ПРОКСИ КАК SOCKS5")
    print("=" * 60)
    print()
    
    proxy_host = "pro.alotaxi.info"
    proxy_port = 4515
    
    print(f"Прокси: {proxy_host}:{proxy_port}")
    print()
    
    try:
        # Попытка подключения через SOCKS5
        proxy = Proxy(
            proxy_type=ProxyType.SOCKS5,
            host=proxy_host,
            port=proxy_port
        )
        
        print("1. Попытка подключения через SOCKS5...")
        
        # Попытка подключиться к Telegram API
        sock = await proxy.connect(
            dest_host="api.telegram.org",
            dest_port=443
        )
        
        print("   [OK] Подключение установлено!")
        sock.close()
        
    except Exception as e:
        print(f"   [ERROR] Ошибка: {type(e).__name__}")
        print(f"   Детали: {str(e)[:200]}")
        print()
        print("ВЫВОД: MTProto прокси не работает как обычный SOCKS5")
        print()
        print("РЕШЕНИЕ:")
        print("MTProto прокси предназначен для Telegram клиентов,")
        print("а не для Bot API через HTTP.")
        print()
        print("Рекомендации:")
        print("1. Используйте обычный SOCKS5/HTTP прокси")
        print("2. Или используйте VPN")
        print("3. Или разверните на VPS за границей")

if __name__ == "__main__":
    asyncio.run(test_mtproto_as_socks())
