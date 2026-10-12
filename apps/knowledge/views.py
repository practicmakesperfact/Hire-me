from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import KnowledgeSource, DocumentChunk
from .serializers import KnowledgeSourceSerializer, DocumentChunkSerializer
from services.rag.document_processor import DocumentProcessor
from services.rag.retriever import KnowledgeRetriever


class KnowledgeSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for knowledge sources."""
    queryset = KnowledgeSource.objects.all()
    serializer_class = KnowledgeSourceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['verification_status']
    
    def get_permissions(self):
        # Only admins can create/update/delete
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Get chunks for a source."""
        source = self.get_object()
        chunks = source.chunks.all().order_by('chunk_index')
        
        serializer = DocumentChunkSerializer(chunks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a source."""
        source = self.get_object()
        processor = DocumentProcessor()
        stats = processor.get_source_stats(source)
        
        return Response(stats)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def import_document_view(request):
    """Import a document as knowledge source."""
    title = request.data.get('title')
    content = request.data.get('content')
    source_url = request.data.get('source_url', '')
    license_info = request.data.get('license_info', '')
    version = request.data.get('version', '')
    description = request.data.get('description', '')
    
    if not title or not content:
        return Response(
            {'error': 'title and content are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    processor = DocumentProcessor()
    
    # Create temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name
    
    try:
        source = processor.import_text_file(
            temp_path,
            title=title,
            source_url=source_url,
            license_info=license_info,
            version=version,
            description=description
        )
        
        if source:
            serializer = KnowledgeSourceSerializer(source)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': 'Failed to import document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    finally:
        import os
        os.unlink(temp_path)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_knowledge_view(request):
    """Search knowledge base."""
    query = request.data.get('query')
    topic = request.data.get('topic')
    limit = request.data.get('limit', 5)
    
    if not query:
        return Response(
            {'error': 'query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    retriever = KnowledgeRetriever()
    results = retriever.search(query, topic=topic, limit=limit)
    
    return Response({
        'query': query,
        'results_count': len(results),
        'results': results
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_answer_view(request):
    """Verify answer against knowledge sources."""
    question = request.data.get('question')
    answer = request.data.get('answer')
    topic = request.data.get('topic')
    
    if not question or not answer:
        return Response(
            {'error': 'question and answer are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    retriever = KnowledgeRetriever()
    verification = retriever.verify_answer_with_sources(
        question, answer, topic or ''
    )
    
    return Response(verification)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def source_list_view(request):
    """Get list of all verified sources."""
    retriever = KnowledgeRetriever()
    sources = retriever.get_source_list()
    
    return Response({
        'count': len(sources),
        'sources': sources
    })
