
from django.contrib import admin
from django.urls import path

from mcq.views.create_mcq_question import create_mcq_question

urlpatterns = [
    path('create', create_mcq_question),
]
