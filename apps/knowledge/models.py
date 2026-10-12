from django.db import models


class KnowledgeSource(models.Model):
    """Approved knowledge source for RAG."""
    title = models.CharField(max_length=300)
    source_url = models.URLField(blank=True)
    license_info = models.CharField(max_length=200, blank=True)
    version = models.CharField(max_length=100, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    import_date = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    content_hash = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'knowledge_sources'
        ordering = ['-import_date']
    
    def __str__(self):
        return self.title


class DocumentChunk(models.Model):
    """Chunked document content for retrieval."""
    source = models.ForeignKey(KnowledgeSource, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content = models.TextField()
    chunk_hash = models.CharField(max_length=64)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_chunks'
        ordering = ['source', 'chunk_index']
        unique_together = ['source', 'chunk_index']
        indexes = [
            models.Index(fields=['source', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"{self.source.title} - Chunk {self.chunk_index}"
