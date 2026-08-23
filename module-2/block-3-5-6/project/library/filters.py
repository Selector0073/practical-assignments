import django_filters

from .models import Book


class BookFilter(django_filters.FilterSet):
    """Filtering for the Book library:

    * ``?genre=poetry``  -> exact genre match
    * ``?author_id=1``   -> books by a specific author (FK exposed as author_id)
    * ``?q=kobzar``      -> case-insensitive partial match on ``title``
    """

    genre = django_filters.CharFilter(lookup_expr='exact')
    author_id = django_filters.NumberFilter(field_name='author')
    q = django_filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Book
        fields = []
