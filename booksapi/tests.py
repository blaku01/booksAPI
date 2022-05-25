from telnetlib import STATUS
from rest_framework.test import APITestCase
from django.urls import reverse
from booksapi.models import Book
from rest_framework import status
# Create your tests here.


class TestApiSpec(APITestCase):

    url = reverse('api_spec')

    def test_api_spec_url(self):
        self.assertEqual(self.url, '/api spec')

    def test_get_api_spec(self):
        expected_spec = {
            "info": {
                "version": "2022.05.16"
            }
        }
        response = self.client.get(self.url)
        self.assertEqual(response.data, expected_spec)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestCRUDBooks(APITestCase):

    url = reverse('books')
    expected_books = [
        {
            "external_id": "rToaogEACAAJ",
            "title": "Hobbit czyli Tam i z powrotem",
            "authors": [
                "J. R. R. Tolkien"
            ],
            "acquired": False,
            "published_year": "2004",
            "thumbnail": "http://books.google.com/books/content?id=YyXoAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"
        },
        {
            "external_id": "EsiJcusIVD",
            "title": "A Middle English Reader",
            "authors": [
                "Kenneth Sisam",
                "J. R. R. Tolkien"
            ],
            "acquired": False,
            "published_year": "2005",
            "thumbnail": None
        }
    ]

    other_books = [
        {
            "external_id": "pscmDwAAQBAJ",
            "title": "Key Terms and Concepts for Investigation",
            "authors": [
                "John J. Fay",
            ],
            "acquired": True,
            "published_year": "2017",
            "thumbnail": "http://books.google.com/books/content?id=pscmDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
        },
        {
            "external_id": "OMOwmLgbMfYC",
            "title": "Out's Gay & Lesbian Guide to the Web",
            "authors": [
                "J. Harrison Fitch"
            ],
            "acquired": False,
            "published_year": "1997",
            "thumbnail": "http://books.google.com/books/content?id=OMOwmLgbMfYC&printsec=frontcover&img=1&zoom=1&source=gbs_api",
        }
    ]

    items = Book.objects.bulk_create(
        [Book(**book_data) for book_data in expected_books + other_books])

    def test_books_url(self):
        self.assertEqual(self.url, '/books')

    def test_get_books(self):
        url = self.url + '?author="Tolkien"&from=2003&to=2022&acquired=false'
        response = self.client.get(url) 
        response_data = response.data
        [book.pop("id") for book in response_data]
        self.assertEqual(response.data, self.expected_books)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_detail(self):
        url = self.url + "/123"
        response = self.client.get(url)
        self.assertEqual(response.data, self.expected_books[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_create(self):
        book_data = {
            "external_id": None,
            "title": "Magiczna księga",
            "authors": [],
            "published_year": "2022",
            "acquired": True,
            "thumbnail": None
        }

        response = self.client.post(self.url, book_data)

        response_data = response.data
        response_keys = list(response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_keys, list(self.other_books[0].keys()))
        response_data.pop('id', None)
        self.assertEqual(response.data, book_data)
    
    def test_book_patch(self):
        url = self.url + "/123"
        patch_data = {"acquired": True}
        response = self.client.patch(url, patch_data)
        response_keys = list(response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_keys, list(self.other_books[0].keys()))
        self.assertEqual(response.data['acquired'], patch_data['acquired'])
    
    def test_book_delete(self):
        url = self.url + "/123"

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK) # might be 204 - no content
    

class TestImportBooks(APITestCase):
    
    url = reverse('import')

    def test_import_url(self):
        self.assertEqual(self.url, '/import')
    
    def test_import_books(self):
        data = {"author": "Daniel Singer"}
        response = self.client.patch(self.url, data)
        response_keys = list(response.data.keys())
        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_keys, ["imported"])

        imported = response_data.pop('imported', 0)

        self.assertNotEqual(imported, 0)

