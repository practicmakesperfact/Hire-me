from rest_framework import serializers
from .models import KnowledgeSource, DocumentChunk


class KnowledgeSourceSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = KnowledgeSource
        fields = [
            'id', 'title', 'source_url', 'license_info', 'version',
            'publication_date', 'import_date', 'verification_status',
            'content_hash', 'description', 'chunk_count'
        ]
        read_only_fields = ['id', 'import_date', 'content_hash']
    
    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DocumentChunkSerializer(serializers.ModelSerializer):
    source_title = serializers.CharField(source='source.title', read_only=True)
    
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'source', 'source_title', 'chunk_index',
            'content', 'chunk_hash', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'chunk_hash', 'created_at']
