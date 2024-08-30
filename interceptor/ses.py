from telethon.sessions import StringSession
import mysql.connector
import logging
from django.conf import settings
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import interceptor.routing


api_id = 24364263
api_hash = "1f03c4f0e8617dd5fe4f16e9d629f47c"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("[asgi] DJANGO_SETTINGS_MODULE := telegram_interceptor.settings")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_interceptor.settings')

# Инициализация Django перед использованием любых моделей или компонентов
logger.info("[asgi] django.setup()")
django.setup()

logger.info("[asgi] interceptor.routing.websocket_urlpatterns = {URLRouter(interceptor.routing.websocket_urlpatterns)}")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            interceptor.routing.websocket_urlpatterns
        )
    ),
})

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

