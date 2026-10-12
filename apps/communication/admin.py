from django.contrib import admin
from .models import CommunicationIssue


@admin.register(CommunicationIssue)
class CommunicationIssueAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'status', 'practice_count', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['user__username', 'original_text']
    readonly_fields = ['created_at', 'reviewed_at']
