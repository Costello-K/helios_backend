from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsOwner, ReadOnly
from common.views import get_serializer_paginate
from company.serializers import InvitationToCompanySerializer, RequestToCompanySerializer
from services.decorators import log_database_changes

from .serializers import UserDetailSerializer, UserSerializer

User = get_user_model()


@log_database_changes
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsOwner | ReadOnly, )
    ordering = ('created_at', )

    def get_queryset(self):
        queryset = User.objects.all()

        queryset = queryset.order_by(*self.ordering)

        return queryset

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return UserDetailSerializer
        return UserSerializer

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_requests(self, request):
        queryset = request.user.my_requests.order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, RequestToCompanySerializer)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_invitations(self, request):
        queryset = request.user.my_invitations.order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, InvitationToCompanySerializer)
