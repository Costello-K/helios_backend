from django.shortcuts import get_object_or_404
from rest_framework import permissions

from company.models import Company
from user.models import RequestToCompany


class ReadOnly(permissions.BasePermission):
    """
    Provides read-only access
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsOwner(permissions.BasePermission):
    """
    Grants access to the object only to the owner
    """
    def has_object_permission(self, request, view, instance):
        return instance == request.user


class IsCompanyOwner(permissions.BasePermission):
    """
    Grants access to the object only to the company owner
    """
    def has_permission(self, request, view):
        if view.action in ['remove_user', 'list']:
            company_pk = request.parser_context.get('kwargs', {}).get('company_pk')

            if company_pk is None:
                return False

            company = get_object_or_404(Company, pk=company_pk)
            return company.is_owner(request.user)

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, instance):
        if hasattr(instance, 'company'):
            return instance.company.is_owner(request.user)
        elif hasattr(instance, 'owner'):
            return instance.is_owner(request.user)
        return False


class IsInvitationRecipient(permissions.BasePermission):
    """
    Grants access to the object only to the recipient
    """
    def has_object_permission(self, request, view, instance):
        return instance.recipient == request.user


class IsRequestSender(permissions.BasePermission):
    """
    Grants access to the object only to the sender
    """
    def has_permission(self, request, view):
        if view.action == 'cancell':
            company_pk = request.parser_context.get('kwargs', {}).get('pk')
            sender_pk = request.parser_context.get('kwargs', {}).get('user_pk')

            if company_pk is None or sender_pk is None:
                return False

            instance = get_object_or_404(RequestToCompany, company_id=company_pk, sender_id=sender_pk)
            return instance.sender == request.user

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, instance):
        return instance.sender == request.user


class IsCompanyOwnerCreateInvitation(permissions.IsAuthenticated):
    """
    Only the company owner can create and revoke invitations
    """
    def has_permission(self, request, view):
        if view.action in ['create', 'revoke']:
            company_pk = request.parser_context.get('kwargs', {}).get('company_pk')

            if company_pk is None:
                return False

            company = get_object_or_404(Company, pk=company_pk)
            return company.is_owner(request.user)

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, instance):
        if hasattr(instance, 'company'):
            return instance.company.is_owner(request.user)
        elif hasattr(instance, 'owner'):
            return instance.is_owner(request.user)
        return False
