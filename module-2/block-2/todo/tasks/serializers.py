from rest_framework import serializers
from .models import Tasks, Category

class TasksModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tasks
        fields = [
            "id", "title", "status", "priority", "category", "created_by"
        ]

class CategoryModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "name"
        ]