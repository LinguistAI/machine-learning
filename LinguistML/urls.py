
from django.contrib import admin
from django.urls import include, path
from LinguistML import settings

from LinguistML.views.ping import ping
from django.views.static import serve 


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf.urls.static import static

import environ


env = environ.Env()
environ.Env.read_env()

BASE_URL_PREFIX = env("BASE_URL_PREFIX", default="api/v1")


schema_view = get_schema_view(
   openapi.Info(
      title="LinguistML API",
      default_version='v1',
      description="API docs for LinguistML",
    #   terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="linguistai@googlegroups.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    # Main app
    path(f"{BASE_URL_PREFIX}/ping", ping),
    
    # Other apps
    path(f'{BASE_URL_PREFIX}/admin/', admin.site.urls, name="admin"),
    path(f'{BASE_URL_PREFIX}/chat/', include('chat.urls'), name="chat"),
    path(f'{BASE_URL_PREFIX}/mcq/', include('mcq.urls'), name="mcq"),
    # path(f'{BASE_URL_PREFIX}/profile/', include('profiling.urls'), name="profiling"),
    
    # Swagger
    path(f'{BASE_URL_PREFIX}/swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(f'{BASE_URL_PREFIX}/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(f'{BASE_URL_PREFIX}/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Static image serving
    # path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    # path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]


# Custom Error Handling (RESTful)
handler404 = 'LinguistML.exception_handlers.custom_404_view'
handler500 = 'LinguistML.exception_handlers.custom_500_view'