from django.contrib.auth.models import AbstractUser
from common.models import TimeStampedModel


class CustomUser(AbstractUser, TimeStampedModel):
    """
    CustomUser class that extends the AbstractUser and TimeStampedModel.
    This class represents a custom user model with additional timestamp fields.
    """
    pass
