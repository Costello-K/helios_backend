from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from .views import server_check

urlpatterns = [
    path('', server_check, name='server_check'),
    path('admin/', admin.site.urls),
    path('v1/', include('api_v1.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
