from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'topic', 'difficulty', 'question_type', 'created_at']
    list_filter = ['difficulty', 'question_type', 'topic']
    search_fields = ['question_text']
    readonly_fields = ['created_at']
