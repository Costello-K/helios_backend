from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from common.constants import InvitationStatus, RequestStatus
from common.exceptions import ObjectAlreadyInInstance, ObjectDoesNotExist, ObjectNotHavePermissions, ObjectNotInInstance
from common.models import TimeStampedModel

User = get_user_model()


class Company(TimeStampedModel):
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    visibility = models.BooleanField(_('visibility'), default=True)
    owner = models.ForeignKey(User, verbose_name=_('owner'), on_delete=models.CASCADE)

    def is_owner(self, user):
        return self.owner == user

    def add_member(self, user):
        if not self.companymember_set.filter(member=user):
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})
        if self.is_owner(user):
            raise ObjectNotHavePermissions({'message': _('The owner cannot be a member of the company.')})
        CompanyMember.objects.create(company=self, member=user)

    @property
    def get_requests(self):
        return self.requesttocompany_set

    @property
    def get_invitations(self):
        return self.invitationtocompany_set

    @classmethod
    def get_members(cls, company_id):
        company = get_object_or_404(cls, id=company_id)
        return company.companymember_set

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
    member = models.ForeignKey(User, verbose_name=_('member'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE)


class InvitationToCompany(TimeStampedModel):
    recipient = models.ForeignKey(
        User, verbose_name=_('recipient'),
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
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        if not CompanyMember.objects.filter(company=self.company, member=self.recipient).exists():
            self.status = InvitationStatus.ACCEPTED.value
            self.save()
            CompanyMember.objects.create(company=self.company, member=self.recipient)
        else:
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})

    def reject(self):
        if self.status == InvitationStatus.PENDING.value:
            self.status = InvitationStatus.REJECTED.value
            self.save()


class RequestToCompany(TimeStampedModel):
    sender = models.ForeignKey(User, verbose_name=_('sender'), on_delete=models.CASCADE)
    company = models.ForeignKey(Company, verbose_name=_('company'), on_delete=models.CASCADE)
    status = models.CharField(
        _('status'),
        choices=[(status.name, status.value) for status in RequestStatus],
        default=RequestStatus.PENDING.value
    )

    def approved(self):
        if self.status != RequestStatus.PENDING.value:
            raise ObjectDoesNotExist({'message': _('The request has already been processed.')})
        if not CompanyMember.objects.filter(company=self.company, member=self.sender).exists():
            self.status = RequestStatus.APPROVED.value
            self.save()
            CompanyMember.objects.create(company=self.company, member=self.sender)
        else:
            raise ObjectAlreadyInInstance({'message': _('The user is already a member of the company.')})

    def declined(self):
        if self.status == RequestStatus.PENDING.value:
            self.status = RequestStatus.DECLINED.value
            self.save()
