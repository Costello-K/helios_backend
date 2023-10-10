from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from .views import server_check
from .yasg import urlpatterns as doc_urls

urlpatterns = [
    path('', server_check, name='server_check'),
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('auth/', include('djoser.social.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include URL patterns for API documentation
urlpatterns += doc_urls

# Including URL patterns for multi-language support
urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
    path('v1/', include('api_v1.urls')),
)
