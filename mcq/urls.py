
from django.contrib import admin
from django.urls import path

from mcq.views.create_mcq_question import create_mcq_question

urlpatterns = [
    path('question/create', create_mcq_question),
    path('test/create', create_mcq_question),
]
