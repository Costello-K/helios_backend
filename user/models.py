from functools import partial

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.enums import RequestStatus
from common.exceptions import ObjectAlreadyInInstance, ObjectDoesNotExist
from common.models import TimeStampedModel
from company.models import Company, CompanyMember
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

    @property
    def my_requests(self):
        return self.requesttocompany_set.all()

    @property
    def my_invitations(self):
        return self.received_invitations.all()


class RequestToCompany(TimeStampedModel):
    sender = models.ForeignKey(get_user_model(), verbose_name=_('sender'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE)
    status = models.CharField(
        _('status'),
        choices=[(status.name, status.value) for status in RequestStatus],
        default=RequestStatus.PENDING.value
    )

    def approve(self):
        if self.status != RequestStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        if not CompanyMember.objects.filter(company=self.company, member=self.sender).exists():
            self.status = RequestStatus.APPROVED.value
            self.save()
            CompanyMember.objects.create(company=self.company, member=self.sender)
        else:
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})

    def reject(self):
        if self.status != RequestStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        self.status = RequestStatus.REJECTED.value
        self.save()

    def cancell(self):
        if self.status != RequestStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        self.status = RequestStatus.CANCELLED.value
        self.save()

    class Meta:
        verbose_name = _('request to company')
        verbose_name_plural = _('requests to companies')
