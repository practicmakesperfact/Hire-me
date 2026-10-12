from django.contrib import admin
from .models import KnowledgeSource, DocumentChunk


@admin.register(KnowledgeSource)
class KnowledgeSourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'verification_status', 'import_date']
    list_filter = ['verification_status']
    search_fields = ['title', 'description']
    readonly_fields = ['import_date', 'content_hash']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'chunk_index', 'created_at']
    list_filter = ['source']
    readonly_fields = ['created_at', 'chunk_hash']
