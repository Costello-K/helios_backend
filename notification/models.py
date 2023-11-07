from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from common.enums import NotificationStatus
from common.models import TimeStampedModel

User = get_user_model()


class Notification(TimeStampedModel):
    recipient = models.ForeignKey(
        User,
        verbose_name=_('user'),
        on_delete=models.SET_NULL,
        null=True,
        related_name='notification_recipient'
    )
    text = models.TextField(_('text'))
    status = models.CharField(
        _('status'),
        choices=[(notification.name, notification.value) for notification in NotificationStatus],
        default=NotificationStatus.SENT.value,
    )

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')

    def update_status(self, status):
        if self.status == NotificationStatus.VIEWED.value:
            raise ValidationError({'message': _('The notification has already been viewed')})
        if status == NotificationStatus.SENT.value:
            raise ValidationError({'message': _('You cannot set this status yourself')})

        self.status = status
        self.save()
