from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from .views import server_check
from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('', server_check, name='server_check'),
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
    path('v1/', include('api_v1.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include URL patterns for API documentation
urlpatterns += doc_urls
