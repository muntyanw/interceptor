import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import interceptor.routing
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_interceptor.settings')

# Инициализация Django перед использованием любых моделей или компонентов
django.setup()

logger = logging.getLogger(__name__)

logger.info("[asgi] interceptor.routing.websocket_urlpatterns = {interceptor.routing.websocket_urlpatterns}")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            interceptor.routing.websocket_urlpatterns
        )
    ),
})
