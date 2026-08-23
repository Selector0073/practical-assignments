from django.db import models


class Author(models.Model):
    name = models.TextField()
    birth_year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['id']

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.TextField()
    genre = models.TextField(blank=True, default='')
    year_published = models.IntegerField(null=True, blank=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='books',
    )
    created_by = models.TextField()

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['id']

    def __str__(self):
        return self.title
