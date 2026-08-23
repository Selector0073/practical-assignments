"""
Domain 1 — Task Manager API.

Endpoints:
    GET    /api/tasks/                    list (filter + search + pagination)
    GET    /api/tasks/my/                 current user's tasks (X-User)
    GET    /api/tasks/<id>/               retrieve
    DELETE /api/tasks/<id>/               delete (author only)
    POST   /api/tasks/<id>/attachment/    attach a file
    GET    /feedback/                     HTML feedback form
    POST   /feedback/                     process HTML form
    GET    /api/feedback/                 list feedback (JSON)
"""
import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from django_filters.rest_framework import DjangoFilterBackend

from .models import Task, Feedback
from .serializers import TaskSerializer, FeedbackSerializer
from .pagination import TaskPagination
from .authentication import XUserAuthentication, XUserPermission
from .exceptions import MissingXUser, ForbiddenTask

ALLOWED_ATTACHMENT_EXTENSIONS = {'.txt', '.pdf', '.png', '.jpg'}
DEFAULT_CONTENT_TYPES = {
    '.txt': 'text/plain',
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
}


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'priority']

    # ------------------------------------------------------------------
    # Listing: filter by status/priority (via django-filter) + a
    # case-insensitive partial `q` search on title + custom pagination.
    # ------------------------------------------------------------------
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # get_paginated_response wraps into {"tasks": [...], "pagination": {...}}
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {'tasks': serializer.data, 'pagination': {'page': 1, 'limit': len(serializer.data), 'total': len(serializer.data), 'pages': 1}},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # GET /api/tasks/my/ — tasks belonging to the current X-User.
    # ------------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='my')
    def my(self, request):
        user = request.headers.get('X-User')
        if not user:
            raise MissingXUser()
        tasks = Task.objects.filter(created_by=user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(
            {'tasks': serializer.data,
             'pagination': {'page': 1, 'limit': len(serializer.data), 'total': len(serializer.data), 'pages': 1}},
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    # DELETE /api/tasks/<id>/ — author only.
    #   401 : X-User header missing
    #   403 : header present but not the task owner
    #   404 : task does not exist
    #   204 : deleted
    # ------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        user = request.headers.get('X-User')
        if not user:
            raise MissingXUser()

        try:
            task = self.get_queryset().get(pk=kwargs.get('pk'))
        except Task.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if task.created_by != user:
            raise ForbiddenTask()

        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # POST /api/tasks/<id>/attachment/ — attach a file to a task.
    #   201 : uploaded
    #   400 : no file / empty filename / disallowed extension
    #   404 : task does not exist
    # ------------------------------------------------------------------
    @action(detail=True, methods=['post'], url_path='attachment',
            parser_classes=[MultiPartParser, FormParser], authentication_classes=[])
    def attachment(self, request, pk=None):
        try:
            task = self.get_queryset().get(pk=pk)
        except Task.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        file_obj = request.FILES.get('file')
        if file_obj is None:
            return Response(
                {'error': 'No file was submitted'}, status=status.HTTP_400_BAD_REQUEST)

        filename = file_obj.name or ''
        if filename == '':
            return Response(
                {'error': 'Filename is empty'}, status=status.HTTP_400_BAD_REQUEST)

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
            return Response(
                {'error': f"File type '{ext or filename}' is not allowed"},
                status=status.HTTP_400_BAD_REQUEST)

        # Trust the server-side extension for the content type, never the raw
        # request Content-Type (which clients control).
        content_type = DEFAULT_CONTENT_TYPES.get(ext, file_obj.content_type)

        task.attachment.save(filename, file_obj, save=True)
        task.attachment_content_type = content_type
        task.save()

        return Response({
            'message': 'File uploaded',
            'filename': filename,
            'content_type': content_type,
            'task_id': task.id,
        }, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Feedback — a single plain Django view mounts BOTH methods at /feedback/:
#   GET  /feedback/ -> render the HTML form (200)
#   POST /feedback/ -> validate + persist, then render a confirmation page
#                      (201 on success, 400 on validation failure)
# The JSON list side is a DRF ListAPIView.
# ---------------------------------------------------------------------------
@csrf_exempt
def feedback_view(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip()
        message = (request.POST.get('message') or '').strip()

        if not (name and email and message):
            return render(request, 'tasks/feedback_form.html', {
                'error': 'All fields (name, email, message) are required.',
                'name': name,
                'email': email,
                'message': message,
            }, status=400)

        feedback = Feedback.objects.create(name=name, email=email, message=message)
        return render(request, 'tasks/feedback_confirmation.html', {
            'feedback': feedback,
        }, status=201)

    return render(request, 'tasks/feedback_form.html')


class FeedbackListView(ListAPIView):
    """GET /api/feedback/ — return all feedback entries as JSON.

    Deliberately disables the Task pagination envelope (which is Task-specific)
    so the response is a plain JSON array of feedback objects.
    """

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    pagination_class = None
