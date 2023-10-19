from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from common.enums import InvitationStatus
from common.exceptions import ObjectAlreadyInInstance, ObjectDoesNotExist, ObjectNotHavePermissions, ObjectNotInInstance
from common.models import TimeStampedModel


class Company(TimeStampedModel):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    visibility = models.BooleanField(_('visibility'), default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), on_delete=models.CASCADE)

    def is_owner(self, user):
        return self.owner == user

    def add_member(self, user):
        if not self.companymember_set.filter(member=user).exists():
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})
        if self.is_owner(user):
            raise ObjectNotHavePermissions({'message': _('The owner cannot be a member of the company.')})
        CompanyMember.objects.create(company=self, member=user)

    def assign_admin(self, user):
        try:
            member = self.companymember_set.get(member=user)
        except CompanyMember.DoesNotExist as err:
            raise ObjectDoesNotExist(
                {'message': _('To be designated as an administrator, a user must be a member of a company.')}
            ) from err
        if member.admin:
            raise ObjectAlreadyInInstance({'message': _('The user is already a company administrator.')})

        member.admin = True
        member.save()

    def remove_admin(self, user):
        member = self.companymember_set.get(member=user)
        if not member or not member.admin:
            raise ObjectNotInInstance({'message': _('The user is not a company administrator.')})

        member.admin = False
        member.save()

    @property
    def get_requests(self):
        return self.requesttocompany_set.all()

    @property
    def get_invitations(self):
        return self.invitationtocompany_set.all()

    @classmethod
    def get_members(cls, company_id):
        company = get_object_or_404(cls, id=company_id)
        return company.companymember_set.all()

    @classmethod
    def get_admins(cls, company_id):
        members = cls.get_members(company_id)
        return members.filter(admin=True)

    @classmethod
    def remove_member(cls, company_id, member):
        company = get_object_or_404(cls, id=company_id)
        try:
            company_member = company.companymember_set.filter(member=member).first()
            company_member.delete()
        except CompanyMember.DoesNotExist as err:
            raise ObjectNotInInstance({'message': _('The user is not a member of this company.')}) from err

    class Meta:
        verbose_name = _('company')
        verbose_name_plural = _('companies')


class CompanyMember(TimeStampedModel):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('member'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE)
    admin = models.BooleanField(_('admin'), default=False)

    class Meta:
        verbose_name = _('company member')
        verbose_name_plural = _('company members')


class InvitationToCompany(TimeStampedModel):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('recipient'),
        on_delete=models.CASCADE,
        related_name='received_invitations'
    )
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE)
    status = models.CharField(
        _('status'),
        choices=[(status.name, status.value) for status in InvitationStatus],
        default=InvitationStatus.PENDING.value
    )

    def accept(self):
        if self.status != InvitationStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The invitation has already been processed.')})
        if CompanyMember.objects.filter(company=self.company, member=self.recipient).exists():
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})

        self.status_update(InvitationStatus.ACCEPTED.value)

        CompanyMember.objects.create(company=self.company, member=self.recipient)

    def status_update(self, status):
        if self.status != InvitationStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The invitation has already been processed.')})
        self.status = status
        self.save()

    class Meta:
        verbose_name = _('invitation to company')
        verbose_name_plural = _('invitations to companies')
