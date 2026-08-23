"""
Root URL configuration for the unified REST API project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Domain 1: Task Manager
    path('', include('tasks.urls')),
    # Domain 2: Personal Notes (sessions)
    path('', include('notes.urls')),
    # Domain 3: Book Library
    path('', include('library.urls')),
]

# Serve uploaded media during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
