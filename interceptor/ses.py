from telethon.sessions import StringSession
import mysql.connector
import logging
from django.conf import settings


api_id = 24364263
api_hash = "1f03c4f0e8617dd5fe4f16e9d629f47c"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки подключения к базе данных из settings.py
db_config = {
    'host': settings.DATABASES['default']['HOST'],
    'user': settings.DATABASES['default']['USER'],
    'password': settings.DATABASES['default']['PASSWORD'],
    'database': settings.DATABASES['default']['NAME']
}
conn = mysql.connector.connect(**db_config)

cursor = conn.cursor()


def load_session(session_name):
    logger.info(f"Загрузка сессии для: {session_name}")
    cursor.execute(
        "SELECT session_string FROM telethon_sessions WHERE session_name = %s",
        (session_name,),
    )
    row = cursor.fetchone()
    if row:
        logger.info("Сессия успешно загружена")
    else:
        logger.warning("Сессия не найдена, будет создана новая")
    return row[0] if row else None


def save_session(session_name, session_string):
    logger.info(f"Сохранение сессии для: {session_name}")
    cursor.execute(
        """
        INSERT INTO telethon_sessions (session_name, session_string)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
        session_string = VALUES(session_string)
        """,
        (session_name, session_string),
    )
    conn.commit()


session_name = "intercept_session"
session_string = load_session(session_name) or ""
session = StringSession(session_string)

channels_to_listen = [
    4593819858, 
    2204843457, 
    1242446516, 
    4517954004, 
    1363028986
]

channels_to_send = ['@MuntyanValery']
