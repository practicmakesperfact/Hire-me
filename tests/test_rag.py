import pytest
import tempfile
from django.urls import reverse
from apps.knowledge.models import KnowledgeSource, DocumentChunk
from services.rag.document_processor import DocumentProcessor
from services.rag.retriever import KnowledgeRetriever


@pytest.mark.django_db
class TestDocumentProcessor:
    
    def test_import_text_file(self):
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Python is a programming language. " * 100)
            temp_path = f.name
        
        try:
            processor = DocumentProcessor(chunk_size=50)
            source = processor.import_text_file(
                temp_path,
                title='Test Document',
                source_url='https://example.com',
                license_info='MIT'
            )
            
            assert source is not None
            assert source.title == 'Test Document'
            assert source.chunks.count() > 0
        finally:
            import os
            os.unlink(temp_path)
    
    def test_duplicate_import_prevented(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            processor = DocumentProcessor()
            
            # First import
            source1 = processor.import_text_file(temp_path, title='Test')
            
            # Second import (same content)
            source2 = processor.import_text_file(temp_path, title='Test')
            
            assert source1.id == source2.id
            assert KnowledgeSource.objects.count() == 1
        finally:
            import os
            os.unlink(temp_path)
    
    def test_get_source_stats(self):
        source = KnowledgeSource.objects.create(
            title='Test',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Test content with five words',
            chunk_hash='def456'
        )
        
        processor = DocumentProcessor()
        stats = processor.get_source_stats(source)
        
        assert stats['chunk_count'] == 1
        assert stats['total_words'] == 5


@pytest.mark.django_db
class TestKnowledgeRetriever:
    
    def test_keyword_search(self):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Python is a high-level programming language',
            chunk_hash='def456'
        )
        
        retriever = KnowledgeRetriever()
        results = retriever.search('Python programming')
        
        assert len(results) > 0
        assert 'Python' in results[0]['content']
    
    def test_search_empty_query(self):
        retriever = KnowledgeRetriever()
        results = retriever.search('')
        
        assert len(results) == 0
    
    def test_get_context_for_question(self):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Python decorators are functions that modify other functions',
            chunk_hash='def456'
        )
        
        retriever = KnowledgeRetriever()
        context = retriever.get_context_for_question('decorator', 'intermediate')
        
        assert 'decorator' in context.lower()
    
    def test_verify_answer_with_sources(self):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            source_url='https://docs.python.org',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Python is a high-level interpreted programming language',
            chunk_hash='def456'
        )
        
        retriever = KnowledgeRetriever()
        verification = retriever.verify_answer_with_sources(
            question='What is Python?',
            answer='Python is a high-level programming language',
            topic='Python'
        )
        
        assert verification['verified'] is True
        assert len(verification['sources']) > 0


@pytest.mark.django_db
class TestKnowledgeAPI:
    
    def test_list_sources(self, authenticated_client):
        KnowledgeSource.objects.create(
            title='Test Doc',
            content_hash='abc123',
            verification_status='verified'
        )
        
        url = reverse('knowledgesource-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_search_knowledge(self, authenticated_client):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Python is a programming language',
            chunk_hash='def456'
        )
        
        url = reverse('knowledge-search')
        response = authenticated_client.post(url, {
            'query': 'Python'
        }, content_type='application/json')
        
        assert response.status_code == 200
        assert response.json()['results_count'] > 0
    
    def test_verify_answer(self, authenticated_client):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            content_hash='abc123',
            verification_status='verified'
        )
        DocumentChunk.objects.create(
            source=source,
            chunk_index=0,
            content='Python is a programming language',
            chunk_hash='def456'
        )
        
        url = reverse('knowledge-verify')
        response = authenticated_client.post(url, {
            'question': 'What is Python?',
            'answer': 'Python is a programming language',
            'topic': 'Python'
        }, content_type='application/json')
        
        assert response.status_code == 200
        assert 'verified' in response.json()
