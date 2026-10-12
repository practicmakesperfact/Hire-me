from django.contrib import admin
from .models import Role, Topic, InterviewSession, InterviewTurn, InterviewEvaluation


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty_level', 'created_at']
    list_filter = ['difficulty_level']
    search_fields = ['name', 'description']


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'topic', 'status', 'created_at']
    list_filter = ['status', 'interview_type', 'difficulty']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'started_at', 'finished_at']


@admin.register(InterviewTurn)
class InterviewTurnAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'turn_number', 'created_at']
    list_filter = ['session__status']
    readonly_fields = ['created_at', 'answered_at']


@admin.register(InterviewEvaluation)
class InterviewEvaluationAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'technical_score', 'created_at']
    readonly_fields = ['created_at']
