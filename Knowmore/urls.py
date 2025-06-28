from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import index, sse_stream, get_manifest, test_stream_async
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='react_app'),
    path('api/stream', sse_stream, name='sse_stream'),
    path('api/test_stream_async', test_stream_async, name='test_stream_async'),
    path('manifest/', get_manifest, name='get_manifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
