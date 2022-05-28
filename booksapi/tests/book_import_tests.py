from rest_framework.test import APITestCase
from rest_framework import status


class TestImportBooks(APITestCase):
    def setUp(self):
        self.url = '/import'

    def test_import_books(self):
        data = {"author": "Daniel Singer"}
        response = self.client.post(self.url, data)
        response_keys = list(response.data.keys())
        response_data = response.data

        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)  # 201_CREATED
        self.assertEqual(response_keys, ["imported"])
        imported = response_data.pop('imported', 0)
        self.assertNotEqual(imported, 0)
        #self.assertEqual(imported, Book.objects.all())
