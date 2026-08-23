from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TaskViewSet, feedback_view, FeedbackListView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('api/', include(router.urls)),
    # Feedback: single view handles GET (form) and POST (submit), plus JSON list
    path('feedback/', feedback_view, name='feedback_form'),
    path('api/feedback/', FeedbackListView.as_view(), name='feedback_list'),
]
