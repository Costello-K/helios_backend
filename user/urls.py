from django.urls import path

from .views import UserViewSet

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path(
        '<int:pk>/',
        UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='user-detail',
    ),
    path('me/requests/', UserViewSet.as_view({'get': 'my_requests'}), name='user-my-requests'),
    path('me/invitations/', UserViewSet.as_view({'get': 'my_invitations'}), name='user-my-invitations'),
]
