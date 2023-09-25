from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from common.permissions import IsOwnerOrReadOnly
from services.decorators import log_database_changes

User = get_user_model()


@log_database_changes
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User objects.

    Attributes:
        queryset (QuerySet): Queryset containing all User objects.
        serializer_class (Serializer): Serializer class for User objects.
        permission_classes (list): Permission classes for controlling access.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        """
        Create a new User object.

        Returns:
            Response: Response with serialized User data if successful, else error response.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # save the new User object to the database
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
