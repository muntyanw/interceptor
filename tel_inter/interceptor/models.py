from django.db import models


class Message(models.Model):
    chat_id = models.CharField(max_length=255)
    message_id = models.IntegerField()
    content = models.TextField()
    edited = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.message_id} from chat {self.chat_id}"
