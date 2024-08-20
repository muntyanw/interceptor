from django.apps import AppConfig


class InterceptorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interceptor'
    def ready(self):
        from .telegram_client import start
        start()