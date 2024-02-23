
from django.contrib import admin
from django.urls import include, path

from chat.views.generate_chat_response import generate_chat_response
from chat.views.get_conversation_messages import get_last_conversation_messages
from chat.views.get_all_conversation_messages import get_all_conversation_messages

urlpatterns = [
    path('send', generate_chat_response),
    path('latest', get_last_conversation_messages),
    path('all', get_all_conversation_messages)
]
