from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.enums import RequestStatus
from common.factories import CompanyFactory, RequestToCompanyFactory, UserFactory

User = get_user_model()


class UserTests(TestCase):
    """
    Tests for user functionality
    """
    def setUp(self):
        """
        Setup method executed before each test method.
        Creates an API client and several users for use in the tests.
        """
        self.client = APIClient()
        # create users in the database
        self.user_1 = User.objects.create_user(**{
            'username': 'test_user_1',
            'first_name': 'Test_1',
            'last_name': 'User_1',
            'email': 'test_1@example.com',
            'password': 'test_password',
        })
        self.user_2 = User.objects.create_user(**{
            'username': 'test_user_2',
            'first_name': 'Test_2',
            'last_name': 'User_2',
            'email': 'test_2@example.com',
            'password': 'test_password',
        })

    def test_create_user(self):
        """
        Test creating a user via the API
        """
        user_data = {
            'username': 'test_user_3',
            'first_name': 'Test_3',
            'last_name': 'User_3',
            'email': 'test_3@example.com',
            'password': 'test_password',
            'confirm_password': 'test_password',
        }
        # send a POST request
        response = self.client.post(reverse('user-list'), user_data, format='json')

        # assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('username'), user_data.get('username'))
        self.assertEqual(response.data.get('email'), user_data.get('email'))

    def test_read_user(self):
        """
        Test reading user information via the API
        """
        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_1.id])
        # send a GET request
        response = self.client.get(url)

        # assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_user(self):
        """
        Test updating user information via the API (without authentication)
        """
        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_1.id])
        # data to update
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User_1',
        }
        # send a PATCH request
        response = self.client.patch(url, updated_data, format='json')

        # assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_non_own_user(self):
        """
        Test of attempt to updating user_1 information via the API (with authentication user_2)
        """
        # perform authentication
        self.client.force_authenticate(user=self.user_2)
        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_1.id])
        # data to update
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User_1',
        }
        # send a PATCH request
        response = self.client.patch(url, updated_data, format='json')

        # assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_authenticated(self):
        """
        Test updating user information via the API by an authenticated user
        """
        # perform authentication
        self.client.force_authenticate(user=self.user_1)

        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_1.id])
        # data to update
        updated_data = {
            'first_name': 'Updated',
            'last_name': 'User_1',
        }
        # send a PATCH request
        response = self.client.patch(url, updated_data, format='json')

        # assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'User_1')

    def test_delete_user(self):
        """
        Test deleting a user via the API (without authentication)
        """
        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_2.id])
        # send a DELETE request
        response = self.client.delete(url)

        # assertions
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_non_own_user(self):
        """
        Test of attempt to deleting a user_1 via the API (with authentication user_2)
        """
        # perform authentication
        self.client.force_authenticate(user=self.user_2)
        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_1.id])
        # send a DELETE request
        response = self.client.delete(url)

        # assertions
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_user_authenticated(self):
        """
        Test deletion of a user via API by an authenticated user
        """
        # perform authentication
        self.client.force_authenticate(user=self.user_2)

        # create a URL for accessing the API endpoint
        url = reverse('user-detail', args=[self.user_2.id])
        # send a DELETE request
        response = self.client.delete(url)

        # assertions
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_users(self):
        """
        Test retrieving a list of users via the API
        """
        # send a GET request
        response = self.client.get(reverse('user-list'))

        # assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['username'], self.user_1.username)
        self.assertEqual(response.data['results'][1]['username'], self.user_2.username)


class RequestToCompanyTests(TestCase):
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

        self.request_1_2 = RequestToCompanyFactory(sender=self.user_1, company=self.company_2)
        self.request_1_3 = RequestToCompanyFactory(sender=self.user_1, company=self.company_3)
        self.request_1_4 = RequestToCompanyFactory(sender=self.user_1, company=self.company_4)
        self.request_2_1 = RequestToCompanyFactory(sender=self.user_2, company=self.company_1)
        self.request_3_1 = RequestToCompanyFactory(sender=self.user_3, company=self.company_1)
        self.request_4_1 = RequestToCompanyFactory(sender=self.user_4, company=self.company_1)

        self.url_request_1_2 = reverse('user-request-detail', args=[self.user_1.id, self.request_1_2.id])

    def test_request_list(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('company-request-list', args=[self.company_1.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_requests = [self.request_2_1.id, self.request_3_1.id, self.request_4_1.id]
        request_from_response = [invitation['id'] for invitation in response.data['results']]
        self.assertEqual(sorted(request_from_response), sorted(expected_requests))

    def test_non_owner_request_list(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('company-request-list', args=[self.company_1.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_request_list(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('user-requests', args=[self.user_1.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)

        expected_requests = [self.request_1_2.id, self.request_1_3.id, self.request_1_4.id]
        request_from_response = [request['id'] for request in response.data['results']]
        self.assertEqual(sorted(request_from_response), sorted(expected_requests))

    def test_create_request(self):
        self.client.force_authenticate(user=self.user_5)
        url = reverse('user-request-detail', args=[self.user_5.id, self.company_1.id])

        response = self.client.post(url, format='json')

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

    def test_update_reject_request(self):
        self.client.force_authenticate(user=self.user_2)
        updated_data = {'confirm': False}

        response = self.client.patch(self.url_request_1_2, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], RequestStatus.REJECTED.value)

    def test_cancell_request(self):
        self.client.force_authenticate(user=self.user_1)
        url = reverse('user-request-cancell', args=[self.user_1.id, self.company_2.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], RequestStatus.CANCELLED.value)

    def test_non_sender_cancell_request(self):
        self.client.force_authenticate(user=self.user_2)
        url = reverse('user-request-cancell', args=[self.user_1.id, self.company_2.id])

        response = self.client.post(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
