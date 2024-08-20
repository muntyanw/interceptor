from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .telegram_client import start
from .models import Message
from .forms import MessageForm

# Представление для запуска бота
def start_bot(request):
    start()
    return HttpResponse("Telegram bot started")

# Представление для редактирования сообщений
def edit_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('message_list')  # Замените 'message_list' на нужное представление или URL
    else:
        form = MessageForm(instance=message)
    
    return render(request, 'interceptor/edit_message.html', {'form': form})
