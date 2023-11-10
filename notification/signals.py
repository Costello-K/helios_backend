from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from quiz.models import Quiz

from .consumers import UserNotificationConsumer
from .models import Notification

channels_layer = get_channel_layer()


@receiver(post_save, sender=Quiz)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        users = instance.company.get_members(instance.company.id)
        notification_text = _('The "{company_name}" company created a new quiz called "{quiz_title}". '
                              'If you want to go through it, go to the company page.'
                              ).format(company_name=instance.company.name, quiz_title=instance.title)
        notifications_data = [Notification(recipient_id=user['member'], text=notification_text) for user in users]

        with transaction.atomic():
            created_notifications = Notification.objects.bulk_create(notifications_data)

            for notification, user in zip(created_notifications, users, strict=True):
                notification_dict = async_to_sync(UserNotificationConsumer.get_validate_data)(notification)
                notification_dict['type'] = 'send_create_notification'

                async_to_sync(channels_layer.group_send)(
                    f'user_{user["member"]}',
                    notification_dict,
                )
