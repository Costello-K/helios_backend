from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from common.enums import NotificationStatus
from common.permissions import IsNotificationRecipient

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = (IsNotificationRecipient, )
    serializer_class = NotificationSerializer
    ordering = ('-created_at',)

    def get_queryset(self):
        recipient_id = self.kwargs.get('user_pk', None)
        if recipient_id is None:
            raise NotFound({'message': _('Page not found.')})

        queryset = Notification.objects.filter(recipient_id=recipient_id)

        queryset = queryset.order_by(*self.ordering)

        return queryset

    @action(detail=True, methods=['post'])
    def set_status_viewed(self, request, user_pk=None, pk=None):
        notification = get_object_or_404(Notification, recipient_id=user_pk, id=pk)
        notification.update_status(NotificationStatus.VIEWED.value)

        serializer = self.get_serializer_class()(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
