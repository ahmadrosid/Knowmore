from django.contrib import admin
from django.urls import path
from .views import index, sse_stream

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('stream/', sse_stream, name='sse_stream'),
]
