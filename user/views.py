from django.contrib.auth import get_user_model
from rest_framework import viewsets

from common.permissions import IsOwnerOrReadOnly
from services.decorators import log_database_changes

from .serializers import UserDetailSerializer, UserSerializer

User = get_user_model()


@log_database_changes
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User objects.

    Attributes:
        queryset (QuerySet): Queryset containing all User objects.
        permission_classes (list): Permission classes for controlling access.
    """
    queryset = User.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        """
        Determine the appropriate serializer class based on the action being performed.
        """
        if self.action in ('retrieve', 'list'):
            return UserDetailSerializer
        return UserSerializer
