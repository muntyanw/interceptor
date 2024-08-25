import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_interceptor.settings')

# Инициализация Django перед использованием любых моделей или компонентов
django.setup()

from interceptor.routing import websocket_urlpatterns # Импортируем маршруты WebSocket из вашего приложения

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
