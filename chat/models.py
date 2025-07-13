# chat/models.py

from django.db import models

class ChatSession(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
