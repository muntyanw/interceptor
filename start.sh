#!/bin/bash
cd /usr/share/nginx/html/interceptor
source venv/bin/activate
uvicorn telegram_interceptor.asgi:application --host 0.0.0.0 --port 8000