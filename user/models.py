from functools import partial

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.enums import RequestStatus
from common.exceptions import ObjectAlreadyInInstance, ObjectDoesNotExist
from common.models import TimeStampedModel
from company.models import Company, CompanyMember
from services.compression_file.compression_image import compress_image_to_given_resolution
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

    @property
    def my_member_companies(self):
        return Company.objects.filter(companymember__member=self)

    @property
    def my_admin_companies(self):
        return Company.objects.filter(companymember__member=self, companymember__admin=True)

    def save(self, *args, **kwargs):
        if self.avatar:
            max_img_resolution = getattr(settings, 'MAX_USER_AVATAR_RESOLUTION', 200)
            width_img, height_img = self.avatar.width, self.avatar.height
            if max(width_img, height_img) > max_img_resolution:
                compressed_content = compress_image_to_given_resolution(self.avatar, max_img_resolution)

                self.avatar.file = SimpleUploadedFile(
                    name=self.avatar.name,
                    content=compressed_content,
                )

        super().save(*args, **kwargs)


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
        if CompanyMember.objects.filter(company=self.company, member=self.sender).exists():
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})

        self.status_update(RequestStatus.APPROVED.value)

        CompanyMember.objects.create(company=self.company, member=self.sender)

    def status_update(self, status):
        if self.status != RequestStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        self.status = status
        self.save()

    class Meta:
        verbose_name = _('request to company')
        verbose_name_plural = _('requests to companies')
