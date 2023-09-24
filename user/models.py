from django.contrib.auth.models import AbstractUser
from services.models_helpers import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
    """
    CustomUser class that extends the AbstractUser and TimeStampedModel.
    This class represents a custom user model with additional timestamp fields.
    """
    pass

    class Meta:
        ordering = ['created_at']
