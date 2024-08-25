import logging
import asyncio
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from . import ses
import os
from channels.layers import get_channel_layer  # для работы с WebSocket
from .logger import logger

# Создание клиента
client = TelegramClient(ses.session, ses.api_id, ses.api_hash)

async def send_message_to_channels(message_text, files):
    logger.info(
        f"[send_message_to_channels] Попытка отправки сообщения: {message_text} с файлами: {files}"
    )
    await asyncio.sleep(1)  
    for channel in ses.channels_to_send:
        if files:
            for file in files:
                logger.info(
                    f"[send_message_to_channels] Отправка файла в канал: {channel}, файл: {file}"
                )
                # Отправка файла с текстом в подписи
                await client.send_file(channel, file, caption=message_text)
                message_text = ""
        else:
            # Если файлов нет, просто отправляем текст
            logger.info(f"[send_message_to_channels] Отправка сообщения в канал: {channel}")
            await client.send_message(channel, message_text)

async def start_client():
    download_directory = "storage/"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)
    
    try:
        logger.debug("[start_client] Попытка подключения к Telegram")
        await client.connect()

        # Проверяем, авторизован ли клиент
        if not await client.is_user_authorized():
            logger.info("[start_client] Клиент не авторизован, завершаем процесс")
            return

        # Сохраняем сессию, если авторизация прошла успешно
        ses.save_session(ses.session_name, client.session.save())
        logger.info("[start_client] Клиент Telethon успешно подключен и авторизован")
        
        @client.on(events.NewMessage(chats=ses.channels_to_listen))
        async def handler(event):
            channel_id = event.chat_id
            logger.info(
                f"[handler] Перехвачено новое сообщение от канала {channel_id}: {event.message.message if event.message else 'Сообщение отсутствует'}"
            )

            message = event.message.message if event.message else "No message"
            sender = await event.get_sender()
            sender_name = sender.first_name if sender else "Unknown"
            file_paths = []

            if event.message.media:
                if isinstance(event.message.media, types.MessageMediaDocument):
                    file_path = await event.message.download_media(file=download_directory)
                    file_paths.append(file_path)
                    logger.info(
                        f"[handler] Файл документа загружен: {file_path} из канала {channel_id}"
                    )
                elif isinstance(event.message.media, types.MessageMediaPhoto):
                    file_path = await event.message.download_media(file=download_directory)
                    file_paths.append(file_path)
                    logger.info(
                        f"[handler] Файл фотографии загружен: {file_path} из канала {channel_id}"
                    )

            logger.info(
                f"[handler] Сообщение из канала {channel_id}: {message}, Отправитель: {sender_name}, Файлы: {file_paths}"
            )

            # Отправка сообщения через WebSocket
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                "telegram_group",
                {
                    "type": "send_new_message",
                    "message": message,
                    "files": file_paths,
                },
            )

        logger.info(
            "[start_client] Обработчики NewMessage зарегистрированы для всех каналов"
        )
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"[start_client] Ошибка при подключении клиента Telethon: {e}")
        raise

async def main():
    logger.info("[main] Запуск основного процесса")
    await start_client()

# Запуск основного процесса в асинхронном режиме
if __name__ == "__main__":
    asyncio.run(main())
