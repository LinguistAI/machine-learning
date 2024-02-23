
from django.contrib import admin
from django.urls import include, path

from chat.views.generate_chat_response import generate_chat_response

urlpatterns = [
    path('', generate_chat_response),
    path('gen/', generate_chat_response),
]
