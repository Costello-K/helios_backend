from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.cache.user_quiz_answers import cache_user_quiz_response
from common.enums import QuizProgressStatus
from common.permissions import (
    FrequencyLimit,
    IsCompanyAdmin,
    IsCompanyMember,
    IsCompanyOwner,
    IsStartedStatus,
    IsUserQuizResultParticipant,
    ReadOnly,
)
from common.views import get_serializer_paginate, get_user_quiz_result_response
from company.models import Company
from quiz.models import Quiz, UserQuizResult
from quiz.serializers import (
    CompanyAnalyticsSerializer,
    QuizAnalyticsSerializer,
    QuizDetailSerializer,
    QuizSerializer,
    UserAnalyticsSerializer,
    UserQuizResultDetailSerializer,
)

from .filters import UserQuizResultFilter

User = get_user_model()


class QuizViewSet(viewsets.ModelViewSet):
    ordering = ('created_at',)

    def get_queryset(self):
        if self.action in ('quizzes_analytics', 'users_analytics', 'user_analytics', 'user_quizzes_list',
                           'user_all_quiz_results', 'company_analytics'):
            return None

        company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

        queryset = Quiz.objects.filter(company=company).order_by(*self.ordering)

        return queryset

    def get_permissions(self):
        permission_classes = (IsCompanyOwner | IsCompanyAdmin | ReadOnly, )

        if self.action in ('quiz_start', ):
            permission_classes = (IsAuthenticated, FrequencyLimit)
        elif self.action in ('quiz_complete', ):
            permission_classes = (IsUserQuizResultParticipant, IsStartedStatus)
        elif self.action in ('user_quiz_results', ):
            permission_classes = (IsUserQuizResultParticipant, )
        elif self.action in ('company_quiz_results', 'company_member_quiz_results'):
            permission_classes = (IsCompanyOwner | IsCompanyAdmin, IsCompanyMember)
        elif self.action in ('quizzes_analytics', 'users_analytics', 'user_analytics', 'user_quizzes_list',
                             'user_all_quiz_results', 'company_analytics'):
            permission_classes = (IsAuthenticated, )

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_class = QuizSerializer

        if self.action in ('retrieve', 'create', 'partial_update', 'quiz_start'):
            serializer_class = QuizDetailSerializer
        elif self.action in ('quiz_complete', 'company_quiz_results', 'company_member_quiz_results',
                             'user_quiz_results', 'user_all_quiz_results'):
            serializer_class = UserQuizResultDetailSerializer
        elif self.action in ('quizzes_analytics', ):
            serializer_class = QuizAnalyticsSerializer
        elif self.action in ('users_analytics', 'user_analytics'):
            serializer_class = UserAnalyticsSerializer
        elif self.action in ('company_analytics', ):
            serializer_class = CompanyAnalyticsSerializer

        return serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()

        company_pk = self.kwargs.get('company_pk', None)
        if company_pk:
            company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

            if IsCompanyOwner().has_object_permission(self.request, self, company) \
                    or IsCompanyAdmin().has_object_permission(self.request, self, company):
                context.update({'full_access': True})

        return context

    @action(detail=False, methods=['get'])
    def user_quizzes(self, request, pk=None):
        if not pk or pk != request.user.id:
            raise NotFound({'message': _('Page not found.')})
        queryset = Quiz.objects.filter(
            Q(company__owner_id=pk) |
            Q(company__companymember__member_id=pk)
        ).distinct().order_by(*self.ordering)
        return get_serializer_paginate(self, queryset, QuizSerializer, context={'request': request})

    @action(detail=True, methods=['post'])
    def quiz_start(self, request, company_pk=None, pk=None):
        if not company_pk or not pk:
            raise NotFound({'message': _('Page not found.')})
        quiz = get_object_or_404(Quiz, id=pk)
        serializer = self.get_serializer_class()(quiz, context={'request': request})
        UserQuizResult.objects.get_or_create(participant=request.user, quiz=quiz, company_id=company_pk,
                                             progress_status=QuizProgressStatus.STARTED.value)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def quiz_complete(self, request, company_pk=None, pk=None):
        if not company_pk or not pk:
            raise NotFound({'message': _('Page not found.')})
        quiz_result = get_object_or_404(UserQuizResult, participant=request.user, quiz_id=pk,
                                        progress_status=QuizProgressStatus.STARTED.value)
        quiz_result.quiz_completed(request.data)
        serializer = self.get_serializer_class()(quiz_result, context={'request': request})
        cache_user_quiz_response(quiz_result, request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def company_quiz_results(self, request, company_pk=None):
        if not company_pk:
            raise NotFound({'message': _('Page not found.')})

        queryset = UserQuizResult.objects.filter(
            participant__in=Company.get_members(company_pk),
            company_id=company_pk,
            progress_status=QuizProgressStatus.COMPLETED.value,
        )

        user_quiz_result_filter = UserQuizResultFilter(request.GET, queryset=queryset)
        queryset = user_quiz_result_filter.qs

        queryset = queryset.order_by(*self.ordering)
        return get_user_quiz_result_response(self, request, queryset, context={'request': request})

    @action(detail=False, methods=['get'])
    def company_member_quiz_results(self, request, company_pk=None, member_pk=None):
        if not company_pk or not member_pk:
            raise NotFound({'message': _('Page not found.')})

        queryset = UserQuizResult.objects.filter(
            participant_id=member_pk,
            company_id=company_pk,
            progress_status=QuizProgressStatus.COMPLETED.value
        ).order_by(*self.ordering)

        return get_user_quiz_result_response(self, request, queryset, context={'request': request})

    @action(detail=False, methods=['get'])
    def user_quiz_results(self, request, company_pk=None, pk=None):
        if not pk:
            raise NotFound({'message': _('Page not found.')})

        queryset = UserQuizResult.objects.filter(
            participant_id=request.user.id,
            quiz_id=pk,
            progress_status=QuizProgressStatus.COMPLETED.value
        ).order_by(*self.ordering)

        return get_user_quiz_result_response(self, request, queryset, context={'request': request})

    @action(detail=False, methods=['get'])
    def quizzes_analytics(self, request):
        queryset = Quiz.objects.all().order_by(*self.ordering)

        serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def users_analytics(self, request):
        queryset = User.objects.all().order_by(*self.ordering)

        serializer = self.get_serializer_class()(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def user_analytics(self, request, pk=None):
        queryset = get_object_or_404(User, id=pk)

        serializer = self.get_serializer_class()(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def company_analytics(self, request, pk=None):
        if not pk:
            raise NotFound({'message': _('Page not found.')})

        queryset = get_object_or_404(Company, id=pk)

        is_owner = IsCompanyOwner().has_object_permission(request, self, queryset)
        is_admin = IsCompanyAdmin().has_object_permission(request, self, queryset)

        if not (is_owner or is_admin):
            return Response({'message': _('Permission Denied')}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer_class()(queryset, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def user_all_quiz_results(self, request, pk=None):
        if not pk or pk != request.user.id:
            raise NotFound({'message': _('Page not found.')})

        queryset = UserQuizResult.objects.filter(
            participant_id=request.user.id,
            progress_status=QuizProgressStatus.COMPLETED.value
        )

        user_quiz_result_filter = UserQuizResultFilter(request.GET, queryset=queryset)
        queryset = user_quiz_result_filter.qs
        queryset = queryset.order_by(*self.ordering)

        return get_user_quiz_result_response(self, request, queryset, context={'request': request})
