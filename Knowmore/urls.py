from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import index, sse_stream, get_manifest, get_models

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='react_app'),
    path('api/stream', sse_stream, name='sse_stream'),
    path('api/models', get_models, name='get_models'),
    path('manifest/', get_manifest, name='get_manifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
