from django.db import models

class TelegramMessage(models.Model):
    chat_id = models.CharField(max_length=255)
    message_id = models.CharField(max_length=255)
    text = models.TextField()
    files = models.JSONField(default=list)  # Список файлов, привязанных к сообщению
    edited_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.message_id} from {self.chat_id}"
