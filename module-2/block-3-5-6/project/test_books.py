"""
Tests for the Book endpoints including filtering.

Uses DRF's ``APIClient`` (the ``client`` fixture). Every test that touches the
DB is wrapped in ``pytest.mark.django_db``. ``created_by`` is always set to
``OWNER_FULL_NAME`` so seeded-author names show up consistently.
"""
import pytest

from django.conf import settings

from library.models import Author, Book

pytestmark = pytest.mark.django_db

OWNER = settings.OWNER_FULL_NAME


class TestBooks:
    def test_get_books_empty(self, client):
        resp = client.get('/api/books/')
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_book(self, client):
        resp = client.post('/api/books/', {
            'title': 'Kobzar',
            'genre': 'poetry',
            'year_published': 1840,
            'created_by': OWNER,
        }, format='json')
        assert resp.status_code == 201
        data = resp.json()
        assert 'id' in data
        assert data['title'] == 'Kobzar'
        assert data['genre'] == 'poetry'
        assert data['year_published'] == 1840
        assert data['created_by'] == OWNER
        assert data['author_id'] is None

    def test_create_book_without_title(self, client):
        resp = client.post('/api/books/', {
            'genre': 'poetry',
            'created_by': OWNER,
        }, format='json')
        assert resp.status_code == 400

    def test_create_book_without_created_by(self, client):
        resp = client.post('/api/books/', {
            'title': 'Kobzar',
            'genre': 'poetry',
        }, format='json')
        assert resp.status_code == 400

    def test_create_book_with_author(self, client):
        author_resp = client.post('/api/authors/', {
            'name': 'Taras Shevchenko', 'birth_year': 1814}, format='json')
        assert author_resp.status_code == 201
        author_id = author_resp.json()['id']

        resp = client.post('/api/books/', {
            'title': 'Kobzar',
            'genre': 'poetry',
            'author_id': author_id,
            'created_by': OWNER,
        }, format='json')
        assert resp.status_code == 201
        data = resp.json()
        assert data['author_id'] == author_id
        assert data['created_by'] == OWNER

    def test_create_book_with_nonexistent_author(self, client):
        resp = client.post('/api/books/', {
            'title': 'Ghost',
            'author_id': 9999,
            'created_by': OWNER,
        }, format='json')
        assert resp.status_code == 400

    def test_get_book_by_id(self, client):
        book = Book.objects.create(title='Kobzar', genre='poetry', created_by=OWNER)
        resp = client.get(f'/api/books/{book.id}/')
        assert resp.status_code == 200
        assert resp.json()['id'] == book.id
        assert resp.json()['title'] == 'Kobzar'

    def test_get_book_not_found(self, client):
        resp = client.get('/api/books/9999/')
        assert resp.status_code == 404

    def test_delete_book(self, client):
        book = Book.objects.create(title='Kobzar', created_by=OWNER)
        resp = client.delete(f'/api/books/{book.id}/')
        assert resp.status_code == 204


class TestBooksFilter:
    @pytest.fixture(autouse=True)
    def seed_books(self, client):
        author_a = Author.objects.create(name='Taras Shevchenko', birth_year=1814)
        author_b = Author.objects.create(name='Ivan Franko', birth_year=1856)
        Book.objects.create(title='Kobzar', genre='poetry', author=author_a, created_by=OWNER)
        Book.objects.create(title='Haidamaky', genre='poetry', author=author_a, created_by=OWNER)
        Book.objects.create(title='Zakhar Berkut', genre='prose', author=author_b, created_by=OWNER)

    def test_filter_by_genre(self, client):
        resp = client.get('/api/books/?genre=poetry')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(b['genre'] == 'poetry' for b in data)

    def test_filter_by_author_id(self, client):
        author = Author.objects.get(name='Taras Shevchenko')
        resp = client.get(f'/api/books/?author_id={author.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(b['author_id'] == author.id for b in data)

    def test_search_by_title(self, client):
        resp = client.get('/api/books/?q=kobzar')
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Kobzar'

    def test_filter_no_results(self, client):
        resp = client.get('/api/books/?genre=nonexistent')
        assert resp.status_code == 200
        assert resp.json() == []
