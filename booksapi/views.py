from booksapi.serializers import BookSerializer
from rest_framework import viewsets
from booksapi.models import Book, Author
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import django_filters.rest_framework
from django.shortcuts import get_object_or_404
from config.settings import BOOKS_API_KEY
import requests
from math import ceil

# Create your views here.

class ApiSpecView(APIView):
    # might store version somewhere else // use openapi.yaml
    def get(self, request, format=None):
        return Response({"info": {"version":"2022.05.16"}}, status=status.HTTP_200_OK)


class BookViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['authors', 'title']

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        authors = data.pop('authors', [])
        serializer = BookSerializer(data=data, many=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        if authors:
            created_authors = [Author.objects.get_or_create(
                full_name=author)[0] for author in authors]
            # may use bulk_create, but it is unlikely that there will be a large number of authors in the same book
            obj.authors.set(*created_authors)
            obj.save()
        serializer_data = serializer.data
        serializer_data['authors'] = authors
        return Response(serializer_data, status=status.HTTP_201_CREATED)


    def get_queryset(self):
        year_from = self.request.query_params.get('from')
        year_to = self.request.query_params.get('to')
        author_name = self.request.query_params.get('author')
        acquired = self.request.query_params.get('acquired')
        query_params = {}
        if year_from is not None:
            query_params["published_year__gte"] = int(year_from)
        if year_to is not None:
            query_params["published_year__lte"] = int(year_to)
        if author_name is not None:
            query_params["authors__full_name__icontains"] = author_name.replace(
                '"', '')
        if acquired is not None:
            if acquired == "false":
                query_params["acquired"] = False
            elif acquired == "true":
                query_params["acquired"] = True
        # a lot of redundant ifs. Rethink
        queryset = Book.objects.filter(**query_params).order_by("id")

        return queryset


class ImportBooksView(APIView):

    def post(self, request, format=None):
        author = request.data.get('author')
        max_results = 40
        base_url = f"https://www.googleapis.com/books/v1/volumes?q=inauthor:'{author}'&maxResults={max_results}&key={BOOKS_API_KEY}"
        res = requests.get(base_url)

        data = res.json().get('items')
        total_books = res.json().get('totalItems')
        for i in range(1, ceil(total_books/max_results)):
            url = base_url + f"&startIndex={i*40}"
            res = requests.get(url)
            data += res.json().get('items', [])
        
        authors_dict = {}
        if res.status_code == 200:
            imported = 0
            for book_data in data:
                external_id = book_data.get('id')
                book_data = book_data.get('volumeInfo')
                published_year = book_data.get('publishedDate')
                title=book_data.get('title')
                if title is not None:
                    imported += 1
                    if published_year is not None:
                        published_year = int(published_year[:4])

                    book_authors = book_data.get('authors', [])
                    image_links = book_data.get('imageLinks')
                    if image_links is not None:
                        thumbnail = image_links.get('thumbnail')
                    else:
                        thumbnail = None
                    for book_author in book_authors:
                        if book_author not in authors_dict.keys():
                            author_obj = Author.objects.get_or_create(full_name=book_author)[0].id
                            authors_dict[book_author] = author_obj
                    book = Book.objects.update_or_create(
                        external_id=external_id,
                        title=book_data.get('title'),
                        published_year=published_year,
                        acquired=False,
                        thumbnail= thumbnail
                        )[0]
                    author_indexes = [authors_dict[author] for author in book_authors]
                    book.authors.set(author_indexes)
            return Response({"imported": imported}, status=status.HTTP_200_OK)



"""         authors_dict = {}
        books = []
        authors_per_book = []
        if res.status_code == 200:
            for book_data in data:
                external_id = book_data.get('id')
                book_data = book_data['volumeInfo']
                published_year = book_data.get('publishedDate')
                if published_year is not None:
                    published_year = int(published_year[:4])
                books.append(
                    Book(
                        external_id=external_id,
                        title=book_data.get('title'),
                        published_year=published_year,
                        acquired=False,
                        thumbnail=book_data['imageLinks']['thumbnail'],
                    )
                )
                book_authors = book_data.get('authors')
                authors_per_book.append(book_authors)
                for book_author in book_authors:
                    if book_author not in authors_dict.keys():
                        author_obj = Author.objects.get_or_create(full_name=book_author)[0].id
                        authors_dict[book_author] = author_obj
            
            book_objects = Book.objects.bulk_create(books)
            for idx, book in enumerate(book_objects):
                author_idx = [authors_dict[author] for author in authors_per_book[idx]]
                book.authors.set(author_idx)
            for book in Book.objects.all():
                print(book.authors.all())
        
        print(len(book_objects))

        return Response({"imported": len(book_objects)}, status=status.HTTP_200_OK)

        // would've to use bulk_create_or_update - might be too many queries - need to ask smb smarter than me
 """