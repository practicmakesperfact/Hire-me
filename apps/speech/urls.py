from django.urls import path
from . import views

urlpatterns = [
    path('transcribe/', views.transcribe_view, name='speech-transcribe'),
    path('synthesize/', views.synthesize_view, name='speech-synthesize'),
    path('analyze/', views.analyze_view, name='speech-analyze'),
]
