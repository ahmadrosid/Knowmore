from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import index, sse_stream, get_manifest, test_tools

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='react_app'),
    path('api/stream', sse_stream, name='sse_stream'),
    path('api/test-tools', test_tools, name='test_tools'),
    path('manifest/', get_manifest, name='get_manifest'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
