
from django.urls import path

from profiling.views.get_user_profile import get_user_profile
from profiling.views.update_user_profile import update_user_profile
from profiling.views.update_ml_profile import update_ml_profile

urlpatterns = [
    path('user', get_user_profile),
    path('update', update_user_profile),
    path('update-ml', update_ml_profile)
]
