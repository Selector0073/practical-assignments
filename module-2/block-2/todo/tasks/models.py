from django.db import models
from common.models import ModelMixin

class Category(models.Model):
    name = models.TextField()

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

class Tasks(ModelMixin):
    STATUS_CHICES = [
        ('todo', 'Todo'),
        ('in_progress', 'In progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.TextField()
    status = models.CharField(choices=STATUS_CHICES)
    priority = models.CharField(choices=PRIORITY_CHICES)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_by = models.TextField()

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"