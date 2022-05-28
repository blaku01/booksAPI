
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status


class TestApiSpec(APITestCase):

    url = reverse('api_spec')

    def test_api_spec_url(self):
        self.assertEqual(self.url, '/api_spec')

    def test_get_api_spec(self):
        expected_spec = {
            "info": {
                "version": "2022.05.16"
            }
        }
        response = self.client.get(self.url)
        self.assertEqual(response.data, expected_spec)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
