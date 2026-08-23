"""
Domain 3 — Book Library API (Authors & Books).

    GET/POST    /api/authors/          list / create
    GET/DELETE  /api/authors/<id>/     retrieve / delete
    GET         /api/authors/<id>/books/  that author's books
    GET/POST    /api/books/            list (filter + search) / create
    GET/DELETE  /api/books/<id>/       retrieve / delete

Deleting an author does NOT cascade-delete their books: the FK is
``on_delete=SET_NULL`` so books remain with ``author_id`` set to ``null``.
"""
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer
from .filters import BookFilter


class NoPagination(PageNumberPagination):
    """Library responses return plain lists (no custom envelope)."""

    page_size = None


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    pagination_class = NoPagination

    @action(detail=True, methods=['get'], url_path='books')
    def books(self, request, pk=None):
        author = get_object_or_404(Author, pk=pk)
        books = author.books.all()
        return Response(BookSerializer(books, many=True).data, status=status.HTTP_200_OK)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = NoPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
