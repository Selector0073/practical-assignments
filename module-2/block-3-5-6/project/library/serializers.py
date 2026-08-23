from rest_framework import serializers

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'birth_year']


class BookSerializer(serializers.ModelSerializer):
    # Expose the FK as ``author_id`` (matches the spec: "author_id (FK to
    # Author)"). Validating against the Author queryset ensures a request that
    # references a non-existent author is rejected with a 400.
    author_id = serializers.PrimaryKeyRelatedField(
        source='author',
        queryset=Author.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'genre', 'year_published', 'author_id', 'created_by']
