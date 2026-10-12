from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'issues', views.CommunicationIssueViewSet, basename='communication-issue')

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/<int:session_id>/', views.analyze_session_view, name='communication-analyze-session'),
    path('summary/', views.issue_summary_view, name='communication-summary'),
]
