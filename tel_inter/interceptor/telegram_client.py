from telethon import TelegramClient, events
from .models import Message

api_id = 24364263
api_hash = '1f03c4f0e8617dd5fe4f16e9d629f47c'
phone_number = '+380987648188'

client = TelegramClient('interceptor', api_id, api_hash)

@client.on(events.NewMessage(chats=-1002023070684)) #@SamCrypto_Master https://t.me/immersion_club   -2023070684
async def handler(event):
    # Перехват сообщения
    message = event.message
    if message.media:
        # Скачиваем медиафайл
        file_path = await message.download_media()

        # Отправляем медиафайл вместе с текстом
        await client.send_file(-4557785947, file_path, caption=message.text)
        await client.send_file('@MuntyanValery', file_path, caption=message.text)
    else:
        # Мгновенная отправка сообщения в целевой чат
        await client.send_message(-4557785947, message.message) #@MuntyanValery https://t.me/+pNo1CeFy5_kxNzMy
        await client.send_message('@MuntyanValery', message.message) #@MuntyanValery https://t.me/+pNo1CeFy5_kxNzMy

async def main():
    await client.start(phone=phone_number)
    me = await client.get_me()  # Проверка, что клиент подключился
    print(f"Logged in as {me.username}")
    await client.send_message('@MuntyanValery', 'Я Interceptor - Начинаю слушать канал, сюда буду отправлять все сообщения.')
    await client.send_message(-4557785947, 'Я Interceptor - Начинаю слушать канал, сюда буду отправлять все сообщения.')
    await client.run_until_disconnected()

def start():
    with client:
        client.loop.run_until_complete(main())