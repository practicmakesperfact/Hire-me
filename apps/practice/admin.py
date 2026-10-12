from django.contrib import admin
from .models import PracticeAttempt, ProgressSnapshot


@admin.register(PracticeAttempt)
class PracticeAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'issue', 'score', 'created_at']
    list_filter = ['user']
    readonly_fields = ['created_at']


@admin.register(ProgressSnapshot)
class ProgressSnapshotAdmin(admin.ModelAdmin):
    list_display = ['user', 'snapshot_date', 'total_issues', 'mastered_issues', 'created_at']
    list_filter = ['user', 'snapshot_date']
    readonly_fields = ['created_at']
