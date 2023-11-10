from django.urls import path

from notification import consumers

websocket_urlpatterns = [
    path('ws/notifications/<int:user_pk>/', consumers.UserNotificationConsumer.as_asgi()),
]
