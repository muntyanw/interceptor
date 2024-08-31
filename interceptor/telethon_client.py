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
from telethon.errors import FloodWaitError
from telethon.tl.types import PeerChannel
from collections import deque
import hashlib
import time

handler_registered = False

# Ограничение на количество хранимых сообщений
MAX_SENT_MESSAGES = 30
sent_messages = deque(maxlen=MAX_SENT_MESSAGES)  # Очередь с ограничением размера

def hash_file(file_path):
    """Вычисляет хэш для файла по его содержимому."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Создание клиента
client = TelegramClient(ses.session, ses.api_id, ses.api_hash)

async def send_message_to_channels(message_text, files):
    logger.info(f"[send_message_to_channels] Попытка отправки сообщения: {message_text} с файлами: {files}")
    await asyncio.sleep(1)

    # Создаем уникальный идентификатор сообщения/файла
    unique_id = message_text if message_text else ""
    if files:
        for file in files:
            unique_id += hash_file(file)  # Добавляем хэш файла к идентификатору

    if unique_id in sent_messages:
        logger.warning("[send_message_to_channels] Сообщение или файл уже были отправлены, пропуск отправки.")
        return

    sent_messages.append(unique_id)  # Добавление уникального идентификатора в очередь

    for channel in channels.channels_to_send:
        entity = await client.get_entity(PeerChannel(channel))
        try:
            if files:
                for file in files:
                    logger.info(f"[send_message_to_channels] Отправка файла в канал: {channel}, файл: {file}")
                    await client.send_file(entity, file, caption=message_text)
                    message_text = ""  # Сброс текста сообщения, чтобы он не повторялся
            else:
                logger.info(f"[send_message_to_channels] Отправка сообщения в канал: {channel}")
                await client.send_message(entity, message_text, parse_mode='HTML')
        except FloodWaitError as e:
            logger.warning(f"[send_message_to_channels] FloodWaitError: {e}. Ожидание {e.seconds} секунд.")
            await asyncio.sleep(e.seconds)  # Ожидание перед повторной отправкой
        except Exception as e:
            logger.error(f"[send_message_to_channels] Ошибка при отправке сообщения: {e}")

    logger.info("[send_message_to_channels] Завершение отправки сообщений и файлов.")
    
    
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
    moderation_if_image = channel_info.get('moderation_if_image', False)
    auto_send_text_message = channel_info.get('auto_send_text_message', False)
    
    logger.info(f"[replace_words]  moderation_if_image = {moderation_if_image}")
    logger.info(f"[replace_words]  auto_send_text_message = {auto_send_text_message}")
    return modified_text, moderation_if_image, auto_send_text_message

def extract_original_id(chat_id):
    # Преобразовываем chat_id в строку для удобства обработки
    chat_id_str = str(chat_id)
    
    # Проверяем, начинается ли строка с '-100' и извлекаем число
    match = re.match(r'-100(\d+)', chat_id_str)
    if match:
        return int(match.group(1))  # Возвращаем ID без префикса, преобразованное в int
    return abs(chat_id)  # Возвращаем оригинальный chat_id, если префикс отсутствует

async def start_client():
    
    global handler_registered
    
    download_directory = "storage/"
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    max_retries = 5
    delay = 10  # Задержка между попытками в секундах

    for attempt in range(max_retries):
        try:
            await client.connect()
            if not await client.is_user_authorized():
                logger.info("[start_client] Клиент не авторизован, завершаем процесс")
                return

            ses.save_session(ses.session_name, client.session.save())
            logger.info("[start_client] Клиент Telethon успешно подключен и авторизован")

            chat_ids = list(channels.channels_to_listen.keys())

             # Регистрируем обработчик, если он еще не был зарегистрирован
            if not handler_registered:
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
                    else:
                        modified_message, moderation_if_image, auto_send_text_message = replace_words(message, chat_id)
                        logger.error(f"[handler] moderation_if_image: {moderation_if_image}, file_paths: {file_paths}, moderation_if_image and file_paths: {moderation_if_image and file_paths}")

                        if (moderation_if_image and file_paths) or not auto_send_text_message:
                            logger.info(f"[handler] Отправка сообщения через WebSocket на фронт человеку")
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
                            logger.info(f"[handler] Автоматическое перенаправление в канал")
                            await send_message_to_channels(modified_message, file_paths)

                logger.info("[start_client] Обработчики NewMessage зарегистрированы для всех каналов")
                handler_registered = True
            await client.run_until_disconnected()
            break  # Выход из цикла попыток при успешном подключении

        except Exception as e:
            logger.error(f"[start_client] Ошибка при подключении клиента Telethon: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Попытка повторного подключения через {delay} секунд... ({attempt + 1}/{max_retries})")
                time.sleep(delay)
            else:
                logger.error("Превышено максимальное количество попыток подключения.")
                raise

async def main():
    logger.info("[main] Запуск основного процесса")
    await start_client()

if __name__ == "__main__":
    asyncio.run(main())
