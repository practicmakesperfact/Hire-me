from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RoleViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'interviews', views.InterviewSessionViewSet, basename='interview')

urlpatterns = [
    path('', include(router.urls)),
]
