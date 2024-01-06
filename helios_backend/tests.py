from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class ServerCheckTestCase(TestCase):
    """
    A test case for the "server_check" endpoint.
    It inherits from Django's TestCase class.
    """
    def test_server_check(self):
        # send a GET request
        response = self.client.get(reverse('server_check'))

        # define the expected response data
        expected_data = {
            'status_code': status.HTTP_200_OK,
            'detail': 'ok',
            'result': 'working',
        }

        # assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)
