from asgiref.sync import sync_to_async
import asyncio
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from . import ses
from . import channels
import os
from channels.layers import get_channel_layer  # для работы с WebSocket
from .logger import logger
from .models import AutoSendMessageSetting
import re

# Создание клиента
client = TelegramClient(ses.session, ses.api_id, ses.api_hash)

async def send_message_to_channels(message_text, files):
    logger.info(
        f"[send_message_to_channels] Попытка отправки сообщения: {message_text} с файлами: {files}"
    )
    await asyncio.sleep(1)
    for channel in channels.channels_to_send:
        if files:
            for file in files:
                logger.info(
                    f"[send_message_to_channels] Отправка файла в канал: {channel}, файл: {file}"
                )
                await client.send_file(channel, file, caption=message_text)
                message_text = ""  # Reset message text to avoid repeated captions
        else:
            logger.info(f"[send_message_to_channels] Отправка сообщения в канал: {channel}")
            await client.send_message(channel, message_text)
            
def replace_words(text, channel_id):
    channel_info = channels.channels_to_listen.get(channel_id, {})
    replacements = channel_info.get('replacements', {})
    
    def replace_match(match):
        word = match.group(0)
        # Проверяем, соответствует ли слово одному из ключей в словаре замен
        for key, value in replacements.items():
            if key in word:
                return value
        return word  # Если совпадений нет, возвращаем слово без изменений

    # Создаем регулярное выражение для поиска "слов" с учетом замен
    pattern = r'\b\w+\b'
    modified_text = re.sub(pattern, replace_match, text)
    return modified_text, channel_info.get('moderation_if_image', False)

def extract_original_id(chat_id):
    # Преобразовываем chat_id в строку для удобства обработки
    chat_id_str = str(chat_id)
    
    # Проверяем, начинается ли строка с '-100' и извлекаем число
    match = re.match(r'-100(\d+)', chat_id_str)
    if match:
        return int(match.group(1))  # Возвращаем ID без префикса, преобразованное в int
    return abs(chat_id)  # Возвращаем оригинальный chat_id, если префикс отсутствует

async def start_client():
    download_directory = "storage/"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    try:
        await client.connect()
        if not await client.is_user_authorized():
            logger.info("[start_client] Клиент не авторизован, завершаем процесс")
            return

        ses.save_session(ses.session_name, client.session.save())
        logger.info("[start_client] Клиент Telethon успешно подключен и авторизован")

        # Assuming channels.channels_to_listen is a dictionary where keys are chat identifiers
        chat_ids = list(channels.channels_to_listen.keys())  # Convert dict_keys to a list

        # You may need to convert chat identifiers from strings or usernames to numeric IDs or InputPeers:
        #resolved_chats = await asyncio.gather(*(client.get_input_entity(chat_id) for chat_id in chat_ids))


        @client.on(events.NewMessage(chats=chat_ids))
        async def handler(event):
            chat_id = extract_original_id(event.chat_id)
            sender = await event.get_sender()
            sender_name = getattr(sender, 'first_name', 'Unknown') if hasattr(sender, 'first_name') else getattr(sender, 'title', 'Unknown')
            file_paths = []

            if event.message.media:
                file_path = await event.message.download_media(file=download_directory)
                file_paths.append(file_path)
                logger.info(f"[handler] Файл загружен: {file_path} из канала {event.chat_id}")

            message = event.message.message if event.message else "No message"
            logger.info(f"[handler] Сообщение из канала {event.chat_id}: {message}, Отправитель: {sender_name}, Файлы: {file_paths}")

            setting = await sync_to_async(AutoSendMessageSetting.objects.first)()
            if setting and setting.is_enabled:
                await send_message_to_channels(message, file_paths)
                #await sync_to_async(setting.save)()
            else:
                modified_message, moderation_if_image = replace_words(message, chat_id)
                
                if moderation_if_image and file_paths:
                    # Отправка сообщения через WebSocket на фронт человеку
                    channel_layer = get_channel_layer()
                    await channel_layer.group_send(
                        "telegram_group",
                        {
                            "type": "send_new_message",
                            "message": modified_message,
                            "files": file_paths,
                        },
                    )
                else:
                     await send_message_to_channels(modified_message, file_paths)   
                

        logger.info("[start_client] Обработчики NewMessage зарегистрированы для всех каналов")
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"[start_client] Ошибка при подключении клиента Telethon: {e}")
        raise

async def main():
    logger.info("[main] Запуск основного процесса")
    await start_client()

if __name__ == "__main__":
    asyncio.run(main())
