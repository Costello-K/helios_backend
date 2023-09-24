from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

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
