from django.contrib.auth import get_user_model
from rest_framework import viewsets

from common.permissions import IsOwnerOrReadOnly
from services.decorators import log_database_changes

from .serializers import UserDetailSerializer, UserSerializer

User = get_user_model()


@log_database_changes
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwnerOrReadOnly, )
    ordering = ('created_at', )

    def get_queryset(self):
        queryset = User.objects.all()

        queryset = queryset.order_by(*self.ordering)

        return queryset

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return UserDetailSerializer
        return UserSerializer
