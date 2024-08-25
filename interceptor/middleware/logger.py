import logging

class LoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
       # Код, выполняемый перед обработкой представлением
        
       # Настройка логирования
       logging.basicConfig(level=logging.INFO)
       logger = logging.getLogger(__name__)

       response = self.get_response(request)

        # Код, выполняемый после обработки представлением

       return response

    # Можно также добавить методы process_view, process_exception, process_template_response, если нужно
