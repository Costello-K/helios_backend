from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions
from rest_framework.exceptions import NotAcceptable

from common.enums import QuizProgressStatus
from company.models import Company
from quiz.models import Quiz, UserQuizResult
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
        if view.action in ['create', 'revoke', 'remove_user', 'list', 'admins', 'appoint_admin', 'remove_admin']:
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


class IsCompanyAdmin(permissions.BasePermission):
    """
    Grants access to the object only to the administrator
    """
    def has_permission(self, request, view):
        if view.action in ['create', 'list']:
            company_pk = request.parser_context.get('kwargs', {}).get('company_pk')

            if company_pk is None:
                return False

            company = get_object_or_404(Company, pk=company_pk)
            return company.companymember_set.filter(member=request.user, admin=True).exists()

        return super().has_permission(request, view)

    def has_object_permission(self, request, view, instance):
        if hasattr(instance, 'company'):
            return instance.company.companymember_set.filter(member=request.user, admin=True).exists()
        elif hasattr(instance, 'owner'):
            return instance.companymember_set.filter(member=request.user, admin=True).exists()
        return False


class FrequencyLimit(permissions.BasePermission):
    """
    Allows access to an object if the user has not exceeded the test frequency
    """
    def has_permission(self, request, view):
        quiz_pk = request.parser_context.get('kwargs', {}).get('pk')

        if quiz_pk is None:
            return False

        quiz = get_object_or_404(Quiz, id=quiz_pk)

        last_completed_user_quiz_result = UserQuizResult.objects.filter(
            participant=request.user, quiz=quiz, progress_status=QuizProgressStatus.COMPLETED.value
        ).order_by('-updated_at').last()

        if last_completed_user_quiz_result and quiz.frequency:
            time_since_last_completion = timezone.now() - last_completed_user_quiz_result.updated_at
            delta_time = timezone.timedelta(days=quiz.frequency) - time_since_last_completion
            if delta_time > timezone.timedelta(0):
                raise NotAcceptable(
                    {'message': _('You have exceeded the limit. The quiz will be available via {}.').format(delta_time)}
                )

        return True


class IsUserQuizResultParticipant(permissions.BasePermission):
    """
    Allows access to the object only to the UserQuizResult participant.
    """
    def has_permission(self, request, view):
        quiz_pk = request.parser_context.get('kwargs', {}).get('pk')

        if quiz_pk is None:
            return False

        return UserQuizResult.objects.filter(participant=request.user, quiz_id=quiz_pk,
                                             progress_status=QuizProgressStatus.STARTED.value).exists()
