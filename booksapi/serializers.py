from rest_framework import serializers
from booksapi.models import Book, Author

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['full_name',]
    
    def to_representation(self, value):
        return value.full_name
    
class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    class Meta:
        model = Book
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        data = super(BookSerializer, self).to_representation(instance)
        data['published_year'] = str(data['published_year'])
        return data