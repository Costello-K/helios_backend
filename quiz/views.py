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
    IsCompanyOwner,
    IsUserQuizResultParticipant,
    ReadOnly,
)
from company.models import Company
from quiz.models import Quiz, UserQuizResult
from quiz.serializers import QuizDetailSerializer, QuizSerializer, UserQuizResultSerializer


class QuizViewSet(viewsets.ModelViewSet):
    ordering = ('created_at',)

    def get_queryset(self):
        company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

        queryset = Quiz.objects.filter(company=company).order_by(*self.ordering)

        return queryset

    def get_permissions(self):
        permission_classes = (IsCompanyOwner | IsCompanyAdmin | ReadOnly, )

        if self.action in ('quiz_start', ):
            permission_classes = (IsAuthenticated, FrequencyLimit)
        elif self.action in ('quiz_complete', ):
            permission_classes = (IsUserQuizResultParticipant, )

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_class = QuizSerializer

        if self.action in ('retrieve', 'create', 'partial_update', 'quiz_start'):
            serializer_class = QuizDetailSerializer
        if self.action == 'quiz_complete':
            serializer_class = UserQuizResultSerializer

        return serializer_class

    def get_serializer_context(self):
        context = super().get_serializer_context()

        company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

        if IsCompanyOwner().has_object_permission(self.request, self, company) \
                or IsCompanyAdmin().has_object_permission(self.request, self, company):
            context.update({'add_right_answer': True})

        return context

    @action(detail=True, methods=['post'])
    def quiz_start(self, request, company_pk=None, pk=None):
        if not company_pk or not pk:
            raise NotFound({'message': _('Page not found.')})
        quiz = get_object_or_404(Quiz, id=pk)
        serializer = self.get_serializer_class()(quiz)
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
        serializer = self.get_serializer_class()(quiz_result)
        cache_user_quiz_response(quiz_result, request.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
