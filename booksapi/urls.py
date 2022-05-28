from booksapi.views import BookViewSet, ImportBooksView, ApiSpecView
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter(trailing_slash=False)
router.register(r'books', BookViewSet, basename='books')
urlpatterns = router.urls
urlpatterns.append(path('import', ImportBooksView.as_view(), name='import'))
urlpatterns.append(path('api_spec', ApiSpecView.as_view(), name='api_spec'))
