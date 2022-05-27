from telnetlib import STATUS
from rest_framework.test import APITestCase
from django.urls import reverse
from booksapi.models import Book, Author
from booksapi.views import BookViewSet
from rest_framework import status
import json
# Create your tests here.


""" class TestApiSpec(APITestCase):

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

 """
class TestCRUDBooks(APITestCase):
    maxDiff = None
    def setUp(self):
        self.list_url = reverse('books-list')

        self.expected_books = [
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
            }
        ]

        self.other_books = [
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
        self.items = Book.objects.bulk_create(
            [Book(**{i:book_data[i] for i in book_data if i!='authors'}) for book_data in self.expected_books + self.other_books]
            )
        author = Author.objects.create(full_name=self.expected_books[0]['authors'])
        self.items[0].authors.add(author)
        
        self.detail_url = reverse('books-detail', kwargs={"pk":self.items[0].id})

    def test_books_url(self):
        self.assertEqual(self.list_url, '/books/')

    def test_get_books(self):
        url = self.list_url + '?author="Tolkien"&from=2003&to=2022&acquired=false'
        response = self.client.get(url) 
        response_data = response.data
        books = [(dict(book), book.pop("id"))[0] for book in response_data]
        self.assertEqual(books, self.expected_books)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_detail(self):
        response = self.client.get(self.detail_url)
        book_dict = vars(self.items[0])
        book_dict.pop('_state')
        self.assertEqual(response.data, vars(self.items[0]))
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


        response = self.client.post(self.list_url, book_data, content_type="application/json")

        response_data = response.data
        response_keys = list(response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response_keys, list(self.other_books[0].keys()))
        response_data.pop('id', None)
        self.assertEqual(response.data, book_data)
    
    def test_book_patch(self):
        patch_data = {"acquired": True}
        response = self.client.patch(self.detail_url, patch_data)
        response_keys = list(response.data.keys())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_keys, list(self.other_books[0].keys()))
        self.assertEqual(response.data['acquired'], patch_data['acquired'])
    
    def test_book_delete(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    

""" class TestImportBooks(APITestCase):
    try:
        url = reverse('import')
    except:
        pass

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

 """