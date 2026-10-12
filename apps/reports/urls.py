from django.urls import path
from . import views

urlpatterns = [
    path('overview/', views.overview_report_view, name='reports-overview'),
    path('communication/', views.communication_report_view, name='reports-communication'),
    path('interviews/', views.interview_report_view, name='reports-interviews'),
    path('snapshot/', views.create_snapshot_view, name='reports-snapshot'),
]
