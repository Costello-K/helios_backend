from django.db import models
from django.utils.translation import gettext_lazy as _
from functools import partial
from django.contrib.auth.models import AbstractUser
from common.models import TimeStampedModel

from services.get_file_path import get_path_with_unique_filename


class CustomUser(AbstractUser, TimeStampedModel):
    """
    CustomUser class that extends the AbstractUser and TimeStampedModel.
    This class represents a custom user model with additional timestamp fields.

    Attributes:
        avatar (ImageField): An image field for user avatars.
            - 'upload_to' specifies the upload path using a custom filename generator function.
            - 'blank=True' allows the field to be optional.
    """
    avatar = models.ImageField(
        _('avatar'),
        upload_to=partial(get_path_with_unique_filename, file_path='images/users/avatars'),
        blank=True,
    )
