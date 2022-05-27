from booksapi.views import BookViewSet, ImportUsersView
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter(trailing_slash=False)
router.register(r'books', BookViewSet, basename='books')
urlpatterns = router.urls
urlpatterns.append(path('import', ImportUsersView.as_view(), name='import'))
