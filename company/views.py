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
        owner_id = self.request.data.get('owner_id', None)
        auth_user_id = self.request.user.id

        if owner_id == 'me' or owner_id == auth_user_id:
            queryset = queryset.filter(owner=auth_user_id)
        elif owner_id:
            queryset = queryset.filter(owner=owner_id, visibility=True)
        else:
            queryset = queryset.filter(visibility=True)

        queryset = queryset.order_by(*self.ordering)

        return queryset
