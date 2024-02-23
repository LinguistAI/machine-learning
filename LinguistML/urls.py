
from django.contrib import admin
from django.urls import include, path
from LinguistML import settings

from LinguistML.views.ping import ping
from django.views.static import serve 
from rest_framework_swagger.views import get_swagger_view

import environ


env = environ.Env()
environ.Env.read_env()

BASE_URL_PREFIX = env("BASE_URL_PREFIX", default="api/v1")



urlpatterns = [
    path(f"{BASE_URL_PREFIX}/ping", ping),
    path(f'{BASE_URL_PREFIX}/admin/', admin.site.urls, name="admin"),
    path(f'{BASE_URL_PREFIX}/chat/', include('chat.urls'), name="chat"),
    path(f'{BASE_URL_PREFIX}/profile/', include('profiling.urls'), name="profiling"),
    
    
    path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 

]


# Custom Error Pages

handler404 = 'LinguistML.exception_handlers.custom_404_view'
handler500 = 'LinguistML.exception_handlers.custom_500_view'