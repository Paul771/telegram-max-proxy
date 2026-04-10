import asyncio
from adapters.telegram import TelegramClient

async def check_telegram_updates():
    print("Проверка обновлений от Telegram...")
    print()
    
    client = TelegramClient('1338219014:AAE_L6rC3XTSyBgvjnYaJu1eqgl499_ue90')
    
    try:
        updates = await client.get_updates(limit=10)
        print(f"Получено обновлений: {len(updates)}")
        print()
        
        if updates:
            print("Последние обновления:")
            for i, update in enumerate(updates[-5:], 1):
                update_id = update.get('update_id')
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg.get('chat', {}).get('id')
                    text = msg.get('text', '[нет текста]')
                    date = msg.get('date')
                    print(f"{i}. Update ID: {update_id}")
                    print(f"   Chat ID: {chat_id}")
                    print(f"   Text: {text[:100]}")
                    print(f"   Date: {date}")
                    print()
        else:
            print("Нет обновлений")
            
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(check_telegram_updates())
