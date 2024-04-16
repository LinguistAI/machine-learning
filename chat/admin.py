from django.contrib import admin

from chat.models import ChatBot, Conversation, Message, UnknownWord

admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(ChatBot)
admin.site.register(UnknownWord)