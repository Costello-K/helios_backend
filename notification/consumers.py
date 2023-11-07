import math

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from django.utils.translation import gettext_lazy as _

from common.enums import NotificationStatus
from common.pagination import SettingsPageNumberPagination
from services.jwt_authenticator import JWTAuthenticator

from .models import Notification

User = get_user_model()


class UserNotificationConsumer(AsyncJsonWebsocketConsumer):
    ordering = ('-created_at', )
    pagination_class = SettingsPageNumberPagination
    pagination_page_size = pagination_class.page_size

    @database_sync_to_async
    def get_notification(self, notification_id):
        return Notification.objects.get(id=notification_id)

    @database_sync_to_async
    def get_notification_list(self):
        return Notification.objects.filter(recipient_id=self.user_id).order_by(*self.ordering)

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_pk']
        self.user_group_name = f'user_{self.user_id}'

        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name,
        )

        await self.accept()

    async def receive_json(self, content, **kwargs):
        access_token = content.get('accessToken', None)
        notification_id = content.get('id', None)

        await self.is_authenticated_or_disconnect(access_token)

        if access_token:
            await self.send_notification_list()
        elif notification_id:
            try:
                notification = await self.get_notification(notification_id)
                notification.status = NotificationStatus.VIEWED.value
                await sync_to_async(notification.save)()

                await self.channel_layer.group_send(
                    self.user_group_name,
                    {
                        'type': 'send_update_notification',
                        'id': notification.id,
                        'text': notification.text,
                        'status': notification.status,
                        'created_at': notification.created_at.isoformat(),
                    }
                )

            except Notification.DoesNotExist:
                await self.send_json({'error': _("A notification with given ID does not exist.")})

    async def send_notification_list(self):
        queryset = await self.get_notification_list()
        total_pages = math.ceil(await sync_to_async(queryset.count)() / self.pagination_page_size)
        count_unviewed_notifications = await sync_to_async(
            queryset.filter(status=NotificationStatus.SENT.value).count
        )()
        pagination_queryset = queryset[:self.pagination_page_size]

        notifications_data = await sync_to_async(
            lambda data: [
                {
                    'id': notification.id,
                    'text': notification.text,
                    'status': notification.status,
                    'created_at': notification.created_at.isoformat(),
                } for notification in data
            ]
        )(pagination_queryset)

        await self.send_json({
            'notifications': notifications_data,
            'count_unviewed_notifications': count_unviewed_notifications,
            'page_size': self.pagination_page_size,
            'total_pages': total_pages,
        })

    async def send_create_notification(self, event):
        await self.send_json({
            'create': event['create'],
            'id': event['id'],
            'text': event['text'],
            'status': event['status'],
            'created_at': event['created_at'],
        })

    async def send_update_notification(self, event):
        await self.send_json({
            'id': event['id'],
            'text': event['text'],
            'status': event['status'],
            'created_at': event['created_at'],
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name,
        )

    async def is_authenticated_or_disconnect(self, access_token=None):
        if access_token:
            user = await JWTAuthenticator(access_token).get_user_from_token()
            self.scope['user'] = user
            await sync_to_async(self.scope['user'].save)()
            close_old_connections()

        if self.scope['user'].is_authenticated and self.scope['user'].id == self.user_id:
            return True

        await self.disconnect()
