from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import server_check

urlpatterns = [
    path('', server_check, name='server_check'),
    path('v1/', include('api_v1.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
