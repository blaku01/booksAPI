from rest_framework.test import APITestCase
from django.urls import reverse
from booksapi.models import Book, Author
from rest_framework import status


class TestCRUDBooks(APITestCase):
    def setUp(self):
        self.list_url = reverse('books-list')
        self.book1 = Book.objects.create(**{
            "external_id": "rToaogEACAAJ",
            "title": "Hobbit czyli Tam i z powrotem",
            "acquired": False,
            "published_year": "2004",
            "thumbnail": "http://books.google.com/books/content?id=YyXoAAAACAAJ&printsec=frontcover&img=1&zoom=1&source=gbs_api"
        })
        self.author1 = Author.objects.create(full_name="J. R. R. Tolkien")
        self.book1.authors.add(self.author1)
        self.author2 = Author.objects.create(full_name="Kenneth Sisam")
        self.book2 = Book.objects.create(
            **{
                "external_id": "EsiJcusIVD",
                "title": "A Middle English Reader",
                "acquired": False,
                "published_year": "2005",
            }
        )
        self.book2.authors.add(self.author2, self.author1)

        self.book3 = Book.objects.create(
            **{
                "external_id": "pscmDwAAQBAJ",
                "title": "Key Terms and Concepts for Investigation",
                "acquired": True,
                "published_year": "2017",
                "thumbnail": "http://books.google.com/books/content?id=pscmDwAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api",
            }
        )
        self.author3 = Author.objects.create(full_name="John J. Fay")
        self.book3.authors.add(self.author3)

        self.book4 = Book.objects.create(
            **{
                "external_id": "OMOwmLgbMfYC",
                "title": "Out's Gay & Lesbian Guide to the Web",
                "acquired": False,
                "published_year": "1997",
                "thumbnail": "http://books.google.com/books/content?id=OMOwmLgbMfYC&printsec=frontcover&img=1&zoom=1&source=gbs_api",
            }
        )
        self.author4 = Author.objects.create(full_name="J. Harrison Fitch")
        self.book4.authors.add(self.author2, self.author4)

        self.url = '/books'
        self.detail_url = f'{self.url}/{str(self.book1.id)}'

    def test_get_books(self):
        response = self.client.get(self.url)
        response_book_ids = [book['id'] for book in response.data]
        self.assertEqual(response_book_ids, [
                         self.book1.id, self.book2.id, self.book3.id, self.book4.id])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_books(self):
        query = '?author="Tolkien"&from=2003&to=2022&acquired=false'
        url = self.url + query
        response = self.client.get(url)
        response_book_ids = [book['id'] for book in response.data]
        self.assertEqual(response_book_ids, [self.book1.id, self.book2.id])
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.book1.id)
        self.assertEqual(list(response.data.keys()), [
                         'id', 'authors', 'external_id', 'title', 'published_year', 'acquired', 'thumbnail'])

    def test_book_create(self):
        book_data = {
            "external_id": None,
            "title": "Magiczna księga",
            "authors": [],
            "published_year": "2022",
            "acquired": True,
            "thumbnail": None
        }

        response = self.client.post(self.url, book_data, format='json')
        response_data = response.data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list(response.data.keys()), [
                         'id', 'authors', 'external_id', 'title', 'published_year', 'acquired', 'thumbnail'])
        response_data.pop('id', None)
        self.assertEqual(response.data, book_data)

    def test_book_patch(self):
        patch_data = {"acquired": True}
        response = self.client.patch(self.detail_url, patch_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(response.data.keys()), [
                         'id', 'authors', 'external_id', 'title', 'published_year', 'acquired', 'thumbnail'])
        self.assertEqual(response.data['acquired'], patch_data['acquired'])

    def test_book_delete(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
