from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.enums import RequestStatus
from common.permissions import IsCompanyOwner, IsOwner, IsRequestSender, ReadOnly
from common.views import get_serializer_paginate
from company.serializers import InvitationToCompanySerializer
from services.decorators import log_database_changes

from .models import RequestToCompany
from .serializers import RequestToCompanySerializer, UserSerializer

User = get_user_model()


@log_database_changes
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsOwner | ReadOnly, )
    ordering = ('created_at', )

    def get_queryset(self):
        queryset = User.objects.all()

        queryset = queryset.order_by(*self.ordering)

        return queryset

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def requests(self, request, pk=None):
        if not pk or pk != request.user.id:
            raise NotFound({'message': _('Page not found.')})
        queryset = request.user.my_requests.order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, RequestToCompanySerializer)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def invitations(self, request, pk=None):
        if not pk or pk != request.user.id:
            raise NotFound({'message': _('Page not found.')})
        queryset = request.user.my_invitations.order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, InvitationToCompanySerializer)


class RequestToCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = RequestToCompanySerializer
    ordering = ('created_at',)

    def get_queryset(self):
        queryset = RequestToCompany.objects.all()
        sender_pk = self.kwargs.get('user_pk', None)
        company_pk = self.kwargs.get('company_pk', None)

        if sender_pk:
            queryset = queryset.filter(sender_id=sender_pk)
        elif company_pk:
            queryset = queryset.filter(company_id=company_pk)

        queryset = queryset.order_by(*self.ordering)

        return queryset

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated]
        elif self.action in ['partial_update', 'update', 'list']:
            permission_classes = [IsCompanyOwner]
        elif self.action == 'cancell':
            permission_classes = [IsRequestSender]
        else:
            permission_classes = [IsCompanyOwner | IsRequestSender]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def cancell(self, request, user_pk=None, pk=None):
        instance = get_object_or_404(RequestToCompany, company_id=pk, sender_id=user_pk)
        instance.status_update(RequestStatus.CANCELLED.value)
        serializer = self.serializer_class(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
