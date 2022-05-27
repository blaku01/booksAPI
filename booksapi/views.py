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
# Create your views here.


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

        {
            "external_id": null,
            "title": "Magiczna księga",
            "authors": [],
            "published_year": "2022",
            "acquired": true,
            "thumbnail": null
        }

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


class ImportUsersView(APIView):

    def post(self, request, format=None):
        author = request.data['author']
        url = f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{author}&key={BOOKS_API_KEY}"
        res = requests.get(url)
        authors_dict = {}
        books = []
        if res.status_code == 200:
            data = res.json()
            data = data['items']
            for book_data in data:
                book_data = book_data['volumeInfo']
                authors = []
                for author_name in book_data['authors']:
                    if author_name not in authors_dict.keys():
                        authors_dict[author_name] = Author.objects.get_or_create(
                            full_name=author_name)[0].id # might use bulk_create but there shouldnt be many authors
                    authors.append(authors_dict[author_name])

                book = Book(
                    title=book_data['title'],
                    published_year=int(book_data['publishedDate'][:4]),
                    acquired=False,
                    thumbnail=book_data['imageLinks']['thumbnail'])
                book.authors.set(authors)
                books.append(book)
                print(books)

        return Response({"imported": 0}, status=status.HTTP_200_OK)
