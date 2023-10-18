from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.permissions import (
    IsCompanyOwner,
    IsCompanyOwnerCreateInvitation,
    IsInvitationRecipient,
    ReadOnly,
)
from common.views import get_serializer_paginate

from .models import Company, InvitationToCompany
from .serializers import (
    CompanyMemberSerializer,
    CompanySerializer,
    InvitationToCompanySerializer,
)

User = get_user_model()


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = (IsCompanyOwner | ReadOnly, )
    ordering = ('created_at', )

    def get_queryset(self):
        queryset = Company.objects.all()
        owner_id = self.request.data.get('user_id', None)

        if owner_id != self.request.user.id:
            queryset = queryset.filter(visibility=True)

        if owner_id:
            queryset = queryset.filter(owner_id=owner_id)

        queryset = queryset.order_by(*self.ordering)

        return queryset

    @action(detail=False, methods=['get'])
    def members(self, request, pk=None):
        queryset = Company.get_members(pk).order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, CompanyMemberSerializer)

    @action(detail=True, methods=['delete'], permission_classes=[IsCompanyOwner])
    def remove_user(self, request, company_pk=None, pk=None):
        member = get_object_or_404(User, pk=pk)
        Company.remove_member(company_pk, member)
        return Response({'message': _('User removed from the company.')}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def remove_me(self, request, pk=None):
        Company.remove_member(pk, request.user)
        return Response({'message': _('User removed from the company.')}, status=status.HTTP_204_NO_CONTENT)


class InvitationToCompanyViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationToCompanySerializer
    ordering = ('created_at',)

    def get_queryset(self):
        company_pk = self.kwargs.get('company_pk')
        return InvitationToCompany.objects.all()\
            .filter(company_id=company_pk)\
            .order_by(*self.ordering)

    def get_permissions(self):
        if self.action in ['create', 'revoke']:
            permission_classes = [IsCompanyOwnerCreateInvitation]
        elif self.action in ['partial_update', 'update']:
            permission_classes = [IsInvitationRecipient]
        elif self.action == 'list':
            permission_classes = [IsCompanyOwner]
        else:
            permission_classes = [IsCompanyOwner | IsInvitationRecipient]

        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['post'])
    def revoke(self, request, company_pk=None, pk=None):
        invitation = get_object_or_404(InvitationToCompany, company_id=company_pk, recipient_id=pk)
        invitation.revoke()
        serializer = self.serializer_class(invitation)
        return Response(serializer.data, status=status.HTTP_200_OK)
