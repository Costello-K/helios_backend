from django.urls import path, include
from .views import server_check

urlpatterns = [
    path('', server_check, name='server_check'),
    path('v1/', include('api_v1.urls')),
]
