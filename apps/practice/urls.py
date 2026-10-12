from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'attempts', views.PracticeAttemptViewSet, basename='practice-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('queue/', views.practice_queue_view, name='practice-queue'),
    path('submit/', views.practice_submit_view, name='practice-submit'),
    path('history/', views.practice_history_view, name='practice-history'),
    path('progress/', views.progress_view, name='practice-progress'),
    path('issues/<int:issue_id>/master/', views.mark_mastered_view, name='practice-mark-mastered'),
    path('issues/<int:issue_id>/reference-audio/', views.generate_reference_audio_view, name='practice-reference-audio'),
]
