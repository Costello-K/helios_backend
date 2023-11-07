from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from quiz.models import Quiz

from .models import Notification

channels_layer = get_channel_layer()


@receiver(post_save, sender=Quiz)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        users = instance.company.get_members(instance.company.id)

        for user in users:
            notification = Notification.objects.create(
                recipient_id=user['member'],
                text=_('The "{company_name}" company created a new quiz called "{quiz_title}". '
                       'If you want to go through it, go to the company page.'
                       ).format(company_name=instance.company.name, quiz_title=instance.title)

            )
            async_to_sync(channels_layer.group_send)(
                f'user_{user["member"]}',
                {
                    'type': 'send_create_notification',
                    'create': created,
                    'id': notification.id,
                    'status': notification.status,
                    'text': notification.text,
                    'created_at': notification.created_at.isoformat(),
                }
            )
