from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from common.permissions import IsCompanyAdmin, IsCompanyOwner, ReadOnly
from company.models import Company
from quiz.models import Quiz
from quiz.serializers import QuizSerializer


class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = (IsCompanyOwner | IsCompanyAdmin | ReadOnly, )
    ordering = ('created_at',)

    def get_queryset(self):
        company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

        queryset = Quiz.objects.filter(company=company).order_by(*self.ordering)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        company = get_object_or_404(Company, id=self.kwargs.get('company_pk'))

        if IsCompanyOwner().has_object_permission(self.request, self, company) \
                or IsCompanyAdmin().has_object_permission(self.request, self, company):
            context.update({'add_right_answer': True})

        return context
