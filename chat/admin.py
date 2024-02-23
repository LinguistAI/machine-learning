from django.contrib import admin

from chat.models import Conversation, Message

admin.register(Conversation)
admin.register(Message)