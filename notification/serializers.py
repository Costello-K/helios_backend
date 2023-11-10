from pydantic import ValidationError
from rest_framework import serializers

from .models import Notification
from .schemas import NotificationSchema


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

    def validate(self, data):
        try:
            NotificationSchema.model_validate(data)
        except ValidationError as error:
            raise serializers.ValidationError(error) from error
