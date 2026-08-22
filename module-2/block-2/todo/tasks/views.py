from rest_framework.decorators import action
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import TasksModelSerializer, CategoryModelSerializer
from .models import Tasks, Category
import pygal
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']

    @action(detail=False, methods=['get'])
    def stats(self, request):
        bar_chart = pygal.HorizontalBar()
        bar_chart.title = 'Todo graphic'
        bar_chart.add("Todo", Tasks.objects.filter(status='todo').count())
        bar_chart.add("In progress", Tasks.objects.filter(status='in_progress').count())
        bar_chart.add("Done", Tasks.objects.filter(status='done').count())
        svg = bar_chart.render()
        return HttpResponse(svg, content_type='image/svg+xml')



class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryModelSerializer

    @action(detail=True, methods=['get'], url_path='tasks')
    def tasks(self, request, pk=None):
        category = self.get_object()
        tasks = Tasks.objects.filter(category=category)

        serializer = TasksModelSerializer(tasks, many=True)
        return Response(serializer.data)
