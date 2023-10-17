from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel

User = get_user_model()


class Company(TimeStampedModel):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    visibility = models.BooleanField(_('visibility'), default=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
