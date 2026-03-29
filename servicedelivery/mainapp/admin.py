from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'message', 'is_staff_reply', 'page', 'timestamp')
    list_filter = ('is_staff_reply', 'page', 'timestamp')
    search_fields = ('name', 'message')
    readonly_fields = ('timestamp',)
