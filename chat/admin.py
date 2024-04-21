from django.contrib import admin

from chat.models import ChatBot, Conversation, Message, UnknownWord

from django.contrib import admin
from .models import Conversation, Message, ChatBot, UnknownWord

class UnknownWordAdmin(admin.ModelAdmin):
    list_display = ('word', 'confidenceLevel', 'email', 'isActive', 'createdDate', 'updatedDate')
    list_filter = ('isActive', 'createdDate', 'updatedDate')
    search_fields = ('word', 'email')

class ChatBotAdmin(admin.ModelAdmin):
    list_display = ('name', 'createdDate', 'updatedDate', 'difficultyLevel')
    list_filter = ('difficultyLevel', 'createdDate')
    search_fields = ('name', 'description')

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'userEmail', 'bot_name', 'createdDate', 'updatedDate')
    list_filter = ('createdDate', 'bot__name')
    search_fields = ('title', 'userEmail')

    def bot_name(self, obj: Conversation):
        return obj.bot.name

class MessageAdmin(admin.ModelAdmin):
    list_display = ('short_message', 'senderEmail', 'senderType', 'createdDate')
    list_filter = ('senderType', 'createdDate')
    search_fields = ('messageText', 'senderEmail')

    def short_message(self, obj: Message):
        return (obj.messageText[:50] + '...') if len(obj.messageText) > 50 else obj.messageText

# Register your models here with the custom admin classes
admin.site.register(UnknownWord, UnknownWordAdmin)
admin.site.register(ChatBot, ChatBotAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)
