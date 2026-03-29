from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, default='Anonymous')
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    page = models.CharField(max_length=50, default='home')

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.name}: {self.message[:50]}"
