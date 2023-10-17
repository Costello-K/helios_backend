from rest_framework import viewsets

from common.permissions import IsCompanyOwnerOrReadOnly

from .models import Company
from .serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = (IsCompanyOwnerOrReadOnly, )
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
