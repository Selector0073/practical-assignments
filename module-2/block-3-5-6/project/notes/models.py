from django.db import models


class Note(models.Model):
    """A personal note owned by a logged-in user (identified by username)."""

    title = models.TextField()
    text = models.TextField()
    author = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['id']

    def __str__(self):
        return self.title
