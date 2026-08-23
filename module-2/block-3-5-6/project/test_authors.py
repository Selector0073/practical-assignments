"""
Tests for the Author endpoints and the Author↔Book relationship.

Uses DRF's ``APIClient`` (the ``client`` fixture from conftest.py) in place of
Flask's test client. Every test is wrapped in ``pytest.mark.django_db`` so
Django's transaction rollback gives a clean slate per test.
"""
import pytest

from django.conf import settings

from library.models import Author, Book

pytestmark = pytest.mark.django_db


class TestAuthors:
    def test_get_authors_empty(self, client):
        resp = client.get('/api/authors/')
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_author(self, client):
        resp = client.post('/api/authors/', {'name': 'Taras Shevchenko', 'birth_year': 1814}, format='json')
        assert resp.status_code == 201
        data = resp.json()
        assert 'id' in data
        assert data['name'] == 'Taras Shevchenko'
        assert data['birth_year'] == 1814

    def test_create_author_without_name(self, client):
        resp = client.post('/api/authors/', {'birth_year': 1814}, format='json')
        assert resp.status_code == 400

    def test_get_author_by_id(self, client):
        author = Author.objects.create(name='Ivan Franko', birth_year=1856)
        resp = client.get(f'/api/authors/{author.id}/')
        assert resp.status_code == 200
        data = resp.json()
        assert data['id'] == author.id
        assert data['name'] == 'Ivan Franko'
        assert data['birth_year'] == 1856

    def test_get_author_not_found(self, client):
        resp = client.get('/api/authors/9999/')
        assert resp.status_code == 404

    def test_delete_author(self, client):
        author = Author.objects.create(name='Lesya Ukrainka', birth_year=1871)
        resp = client.delete(f'/api/authors/{author.id}/')
        assert resp.status_code == 204
        # Re-GET must now return 404.
        resp = client.get(f'/api/authors/{author.id}/')
        assert resp.status_code == 404

    def test_delete_author_not_found(self, client):
        resp = client.delete('/api/authors/9999/')
        assert resp.status_code == 404

    def test_delete_author_keeps_books(self, client):
        """Deleting an author must NOT cascade-delete their books: books
        remain but author_id becomes null (ON DELETE SET NULL)."""
        author = Author.objects.create(name='Taras Shevchenko', birth_year=1814)
        Book.objects.create(
            title='Kobzar',
            genre='poetry',
            author=author,
            created_by=settings.OWNER_FULL_NAME,
        )

        resp = client.delete(f'/api/authors/{author.id}/')
        assert resp.status_code == 204

        # The book must still exist with author_id now null.
        book = Book.objects.get(title='Kobzar')
        book_resp = client.get(f'/api/books/{book.id}/')
        assert book_resp.status_code == 200
        assert book_resp.json()['author_id'] is None


class TestAuthorBooks:
    def test_get_author_books(self, client):
        author = Author.objects.create(name='Taras Shevchenko', birth_year=1814)
        Book.objects.create(title='Kobzar', genre='poetry', author=author,
                            created_by=settings.OWNER_FULL_NAME)
        Book.objects.create(title='Haidamaky', genre='poetry', author=author,
                            created_by=settings.OWNER_FULL_NAME)

        resp = client.get(f'/api/authors/{author.id}/books/')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(b['author_id'] == author.id for b in data)

    def test_get_author_books_empty(self, client):
        author = Author.objects.create(name='Ivan Franko', birth_year=1856)
        resp = client.get(f'/api/authors/{author.id}/books/')
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_author_books_not_found(self, client):
        resp = client.get('/api/authors/9999/books/')
        assert resp.status_code == 404
