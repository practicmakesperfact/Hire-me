from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sources', views.KnowledgeSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('import/', views.import_document_view, name='knowledge-import'),
    path('search/', views.search_knowledge_view, name='knowledge-search'),
    path('verify/', views.verify_answer_view, name='knowledge-verify'),
    path('list/', views.source_list_view, name='knowledge-list'),
]
