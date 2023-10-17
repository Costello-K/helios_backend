from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.constants import InvitationStatus, RequestStatus

from .models import Company, CompanyMember, InvitationToCompany, RequestToCompany

User = get_user_model()


class CompanyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = User.objects.create_user(username='user1', password='password')
        self.user_2 = User.objects.create_user(username='user2', password='password')
        self.user_3 = User.objects.create_user(username='user3', password='password')
        self.user_4 = User.objects.create_user(username='user4', password='password')

        self.company_1 = Company.objects.create(name='Company 1', owner=self.user_1, description='description_1')
        self.company_2 = Company.objects.create(name='Company 2', owner=self.user_2)

        CompanyMember.objects.create(company=self.company_2, member=self.user_1)
        CompanyMember.objects.create(company=self.company_2, member=self.user_3)
        CompanyMember.objects.create(company=self.company_2, member=self.user_4)

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

    def test_delete_company_non_company_owner(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.delete(self.company_1_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_company_members(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('company-members', args=[self.company_2.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        results = response.data['results']
        self.assertIn(self.user_1.id, [member['member']['id'] for member in results])
        self.assertIn(self.user_3.id, [member['member']['id'] for member in results])
        self.assertIn(self.user_4.id, [member['member']['id'] for member in results])

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

        self.user_1 = User.objects.create_user(username='user1', password='password')
        self.user_2 = User.objects.create_user(username='user2', password='password')
        self.user_3 = User.objects.create_user(username='user3', password='password')
        self.user_4 = User.objects.create_user(username='user4', password='password')
        self.user_5 = User.objects.create_user(username='user5', password='password')

        self.company_1 = Company.objects.create(name='Company 1', owner=self.user_1)
        self.company_2 = Company.objects.create(name='Company 2', owner=self.user_2)
        self.company_3 = Company.objects.create(name='Company 3', owner=self.user_3)
        self.company_4 = Company.objects.create(name='Company 4', owner=self.user_4)

        self.invitation_1_2 = InvitationToCompany.objects.create(company=self.company_1, recipient=self.user_2)
        self.invitation_1_3 = InvitationToCompany.objects.create(company=self.company_1, recipient=self.user_3)
        self.invitation_1_4 = InvitationToCompany.objects.create(company=self.company_1, recipient=self.user_4)
        self.invitation_2_1 = InvitationToCompany.objects.create(company=self.company_2, recipient=self.user_1)
        self.invitation_3_1 = InvitationToCompany.objects.create(company=self.company_3, recipient=self.user_1)
        self.invitation_4_1 = InvitationToCompany.objects.create(company=self.company_4, recipient=self.user_1)

        self.url_invitation_company_1 = reverse('company-invitation-list', args=[self.company_1.id])
        self.url_invitation_1_2 = reverse('company-invitation-detail', args=[self.company_1.id, self.invitation_1_2.id])

        self.invitation_data = {
            'recipient': self.user_5.id,
            'company': self.company_1.id,
        }

    def test_invitation_list(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.get(self.url_invitation_company_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_invitations = [self.invitation_1_2.id, self.invitation_1_3.id, self.invitation_1_4.id]
        invitation_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(invitation_from_response), sorted(expected_invitations))

    def test_my_invitation_list(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('user-my-invitations')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_invitations = [self.invitation_2_1.id, self.invitation_3_1.id, self.invitation_4_1.id]
        invitation_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(invitation_from_response), sorted(expected_invitations))

    def test_create_invitation(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(self.url_invitation_company_1, self.invitation_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['recipient']['id'], self.user_5.id)

    def test_non_owner_create_invitation(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(self.url_invitation_company_1, self.invitation_data, format='json')

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

    def test_update_reject_invitation(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': False}

        response = self.client.patch(self.url_invitation_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], InvitationStatus.REJECTED.value)

    def test_cancel_invitation(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.delete(self.url_invitation_1_2)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RequestToCompanyTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_1 = User.objects.create_user(username='user1', password='password')
        self.user_2 = User.objects.create_user(username='user2', password='password')
        self.user_3 = User.objects.create_user(username='user3', password='password')
        self.user_4 = User.objects.create_user(username='user4', password='password')
        self.user_5 = User.objects.create_user(username='user5', password='password')

        self.company_1 = Company.objects.create(name='Company 1', owner=self.user_1)
        self.company_2 = Company.objects.create(name='Company 2', owner=self.user_2)
        self.company_3 = Company.objects.create(name='Company 3', owner=self.user_3)
        self.company_4 = Company.objects.create(name='Company 4', owner=self.user_4)

        self.request_1_2 = RequestToCompany.objects.create(sender=self.user_1, company=self.company_2)
        self.request_1_3 = RequestToCompany.objects.create(sender=self.user_1, company=self.company_3)
        self.request_1_4 = RequestToCompany.objects.create(sender=self.user_1, company=self.company_4)
        self.request_2_1 = RequestToCompany.objects.create(sender=self.user_2, company=self.company_1)
        self.request_3_1 = RequestToCompany.objects.create(sender=self.user_3, company=self.company_1)
        self.request_4_1 = RequestToCompany.objects.create(sender=self.user_4, company=self.company_1)

        self.url_request_company_1 = reverse('company-request-list', args=[self.company_1.id])
        self.url_request_1_2 = reverse('company-request-detail', args=[self.company_2.id, self.request_1_2.id])

        self.request_data = {
            'sender': self.user_5.id,
            'company': self.company_1.id,
        }

    def test_request_list(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(self.url_request_company_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_requests = [self.request_2_1.id, self.request_3_1.id, self.request_4_1.id]
        request_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(request_from_response), sorted(expected_requests))

    def test_my_request_list(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('user-my-requests')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_requests = [self.request_1_2.id, self.request_1_3.id, self.request_1_4.id]
        request_from_response = [request['id'] for request in response.data['results']]
        self.assertEqual(sorted(request_from_response), sorted(expected_requests))

    def test_create_request(self):
        self.client.force_authenticate(user=self.user_5)

        response = self.client.post(self.url_request_company_1, self.request_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender']['id'], self.user_5.id)

    def test_update_approve_request(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_request_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], RequestStatus.APPROVED.value)

    def test_sender_update_request(self):
        self.client.force_authenticate(user=self.user_1)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_request_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_update_request(self):
        self.client.force_authenticate(user=self.user_5)
        updated_data = {'confirm': True}

        response = self.client.patch(self.url_request_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_declined_request(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': False}

        response = self.client.patch(self.url_request_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], RequestStatus.DECLINED.value)

    def test_cancel_request(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.delete(self.url_request_1_2)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
