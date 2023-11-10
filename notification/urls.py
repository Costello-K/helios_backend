from django.urls import path

from .views import NotificationViewSet

urlpatterns = [
    path(
        '<int:user_pk>/notifications/',
        NotificationViewSet.as_view({'get': 'list'}),
        name='notification-list',
    ),
    path(
        '<int:user_pk>/notifications/<int:pk>/view/',
        NotificationViewSet.as_view({'post': 'set_status_viewed'}),
        name='set-status-viewed',
    ),
]
