from django.contrib import admin
from .models import Tasks, Category

admin.site.register(Tasks)
admin.site.register(Category)