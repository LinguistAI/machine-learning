from django.contrib import admin

from chat.models import ChatBot, Conversation, Message

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(ChatBot)