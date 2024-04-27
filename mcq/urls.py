
from django.urls import path

from mcq.views.use_item import use_item
from mcq.views.answer_mcq_question import answer_mcq_question
from mcq.views.create_mcq_test import create_mcq_test
from mcq.views.get_mcq_info import get_mcq_info
from mcq.views.get_mcq_question import get_mcq_question
from mcq.views.finish_mcq_test import finish_mcq_test
from mcq.views.get_user_mcq_list import get_user_mcq_list

urlpatterns = [
    # path('question/create', get_mcq_question),
    path('test/create', create_mcq_test),
    path('test/finish', finish_mcq_test),
    path('question/answer', answer_mcq_question),
    path("test/user", get_user_mcq_list),
    path("test/use-item", use_item),
    path("test/<str:test_id>", get_mcq_info),

]
