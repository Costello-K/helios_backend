from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.enums import InvitationStatus
from tests.test_models import (
    CompanyFactory,
    CompanyMemberAdminFactory,
    CompanyMemberFactory,
    InvitationToCompanyFactory,
    UserFactory,
)

from .models import Company, CompanyMember

User = get_user_model()


class CompanyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.user_4 = UserFactory()

        self.company_1 = CompanyFactory(owner=self.user_1)
        self.company_2 = CompanyFactory(owner=self.user_2)

        CompanyMemberFactory(company=self.company_2, member=self.user_1)
        CompanyMemberFactory(company=self.company_2, member=self.user_3)
        CompanyMemberFactory(company=self.company_2, member=self.user_4)

        self.company_1_url = reverse('company-detail', args=[self.company_1.id])

        self.updated_data = {
            'name': 'Updated Company',
            'description': 'Updated description',
        }

    def test_create_company(self):
        self.client.force_authenticate(user=self.user_2)
        company_data = {'name': 'New Company'}

        response = self.client.post(reverse('company-list'), company_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], company_data['name'])
        self.assertEqual(response.data['owner']['id'], self.user_2.id)

    def test_read_company(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.get(self.company_1_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.company_1.name)

    def test_update_company(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.patch(self.company_1_url, self.updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.updated_data['name'])
        self.assertEqual(response.data['description'], self.updated_data['description'])

    def test_update_company_non_company_owner(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.patch(self.company_1_url, self.updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_company(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.delete(self.company_1_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Company.objects.filter(id=self.company_1.id).exists())

    def test_delete_company_non_company_owner(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.delete(self.company_1_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Company.objects.filter(id=self.company_1.id).exists())

    def test_get_company_members(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('company-members', args=[self.company_2.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_members = [self.user_1.id, self.user_3.id, self.user_4.id]
        members_from_response = [member['member']['id'] for member in response.data['results']]
        self.assertEqual(sorted(members_from_response), sorted(expected_members))

    def test_leave_company(self):
        self.client.force_authenticate(user=self.user_3)
        url = reverse('company-remove-me', args=[self.company_2.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CompanyMember.objects.filter(company=self.company_2, member=self.user_3).exists())

    def test_remove_user_from_company(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('company-remove-user', kwargs={'company_pk': self.company_2.id, 'pk': self.user_4.id})

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CompanyMember.objects.filter(company=self.company_2, member=self.user_4).exists())

    def test_remove_user_from_company_non_company_owner(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('company-remove-user', args=[self.company_2.id, self.user_4.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CompanyMember.objects.all().filter(company=self.company_2, member=self.user_4).exists())


class InvitationToCompanyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.user_4 = UserFactory()
        self.user_5 = UserFactory()

        self.company_1 = CompanyFactory(owner=self.user_1)
        self.company_2 = CompanyFactory(owner=self.user_2)
        self.company_3 = CompanyFactory(owner=self.user_3)
        self.company_4 = CompanyFactory(owner=self.user_4)

        self.invitation_1_2 = InvitationToCompanyFactory(company=self.company_1, recipient=self.user_2)
        self.invitation_1_3 = InvitationToCompanyFactory(company=self.company_1, recipient=self.user_3)
        self.invitation_1_4 = InvitationToCompanyFactory(company=self.company_1, recipient=self.user_4)
        self.invitation_2_1 = InvitationToCompanyFactory(company=self.company_2, recipient=self.user_1)
        self.invitation_3_1 = InvitationToCompanyFactory(company=self.company_3, recipient=self.user_1)
        self.invitation_4_1 = InvitationToCompanyFactory(company=self.company_4, recipient=self.user_1)

        self.url_invitation_company_1 = reverse('company-invitation-list', args=[self.company_1.id])
        self.url_invitation_1_2 = reverse('company-invitation-detail', args=[self.company_1.id, self.invitation_1_2.id])

    def test_invitation_list(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(self.url_invitation_company_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_invitations = [self.invitation_1_2.id, self.invitation_1_3.id, self.invitation_1_4.id]
        invitation_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(invitation_from_response), sorted(expected_invitations))

    def test_non_owner_invitation_list(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.get(self.url_invitation_company_1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_invitation_list(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('user-invitations', args=[self.user_1.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_invitations = [self.invitation_2_1.id, self.invitation_3_1.id, self.invitation_4_1.id]
        invitation_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(invitation_from_response), sorted(expected_invitations))

    def test_create_invitation(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('company-invitation-detail', args=[self.company_1.id, self.user_5.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recipient']['id'], self.user_5.id)

    def test_non_owner_create_invitation(self):
        self.client.force_authenticate(user=self.user_3)
        url = reverse('company-invitation-detail', args=[self.company_1.id, self.user_5.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_accept_invitation(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_invitation_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], InvitationStatus.ACCEPTED.value)

    def test_owner_update_invitation(self):
        self.client.force_authenticate(user=self.user_1)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_invitation_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_update_invitation(self):
        self.client.force_authenticate(user=self.user_5)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_invitation_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_decline_invitation(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': False}

        response = self.client.patch(self.url_invitation_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], InvitationStatus.DECLINED.value)

    def test_revoke_invitation(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('company-invitation-revoke', args=[self.company_2.id, self.user_1.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], InvitationStatus.REVOKED.value)

    def test_non_owner_revoke_invitation(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('company-invitation-revoke', args=[self.company_2.id, self.user_1.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CompanyAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.user_4 = UserFactory()
        self.user_5 = UserFactory()
        self.user_6 = UserFactory()

        self.company_1 = CompanyFactory(owner=self.user_1)

        self.member_company_2_1 = CompanyMemberAdminFactory(company=self.company_1, member=self.user_2)
        self.member_company_3_1 = CompanyMemberAdminFactory(company=self.company_1, member=self.user_3)
        self.member_company_4_1 = CompanyMemberAdminFactory(company=self.company_1, member=self.user_4)

        self.member_company_5_1 = CompanyMemberFactory(company=self.company_1, member=self.user_5)

        self.url_admin_list_1 = reverse('company-admins', args=[self.company_1.id])
        self.url_appoint_admin_1_5 = reverse('company-appoint-admin', args=[self.company_1.id, self.user_5.id])
        self.url_remove_admin_4_1 = reverse('company-remove-admin', args=[self.company_1.id, self.user_4.id])

    def test_admin_list(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(self.url_admin_list_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_admins = [self.user_2.id, self.user_3.id, self.user_4.id]
        admins_from_response = [user['member']['id'] for user in response.data['results']]
        self.assertEqual(sorted(admins_from_response), sorted(expected_admins))

    def test_non_owner_admin_list(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.get(self.url_admin_list_1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_appoint_admin(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_appoint_admin_1_5)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyMember.objects.filter(member=self.user_5, admin=True).exists())

    def test_non_owner_appoint_admin(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.post(self.url_appoint_admin_1_5)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CompanyMember.objects.filter(member=self.user_5, admin=True).exists())

    def test_appoint_admin_non_member(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('company-appoint-admin', args=[self.company_1.id, self.user_6.id])

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(CompanyMember.objects.filter(member=self.user_6, admin=True).exists())

    def test_remove_admin(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_remove_admin_4_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyMember.objects.filter(member=self.user_4, admin=False).exists())

    def test_non_owner_remove_admin(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.post(self.url_remove_admin_4_1)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(CompanyMember.objects.filter(member=self.user_4, admin=False).exists())
