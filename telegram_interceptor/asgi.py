import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from  interceptor.routing import websocket_urlpatterns
import logging
from interceptor.ses import session_name, load_session, api_id, api_hash
from telethon import TelegramClient, errors
from telethon.sessions import StringSession


logger = logging.getLogger(__name__)

logger.info("[asgi] DJANGO_SETTINGS_MODULE := telegram_interceptor.settings")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_interceptor.settings')

# Инициализация Django перед использованием любых моделей или компонентов
logger.info("[asgi] django.setup()")
django.setup()

logger.info(f"[asgi] interceptor.routing.websocket_urlpatterns = {websocket_urlpatterns}")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})

logger.info("[asgi] коннект клиента телеграмма")
session_name = session_name
session_string = load_session(session_name)
client = TelegramClient(StringSession(session_string), api_id, api_hash)
client.connect()
logger.info("[asgi] попытка client.connect")
#if not await client.is_user_authorized()
        

