from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.interviews.urls')),
    path('api/v1/', include('apps.questions.urls')),
    path('api/v1/', include('apps.knowledge.urls')),
    path('api/v1/speech/', include('apps.speech.urls')),
    path('api/v1/communication/', include('apps.communication.urls')),
    path('api/v1/practice/', include('apps.practice.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]
