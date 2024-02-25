
from django.urls import path

from profiling.views.get_user_profile import get_user_profile

urlpatterns = [
    path('user', get_user_profile),
]
