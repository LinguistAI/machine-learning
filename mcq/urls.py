
from django.contrib import admin
from django.urls import path

from mcq.views.answer_mcq_question import answer_mcq_question
from mcq.views.create_mcq_test import create_mcq_test
from mcq.views.get_mcq_question import get_mcq_question

urlpatterns = [
    path('question/create', get_mcq_question),
    path('test/create', create_mcq_test),
    path('test/answer', answer_mcq_question),
]
