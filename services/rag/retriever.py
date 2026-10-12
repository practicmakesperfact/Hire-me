import logging
from typing import List, Dict, Any, Optional
from django.db.models import Q
from apps.knowledge.models import KnowledgeSource, DocumentChunk

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    """Retrieve relevant knowledge chunks using FTS5."""
    
    def __init__(self):
        pass
    
    def search(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 5,
        min_relevance: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant document chunks.
        
        Uses SQLite FTS5 if available, otherwise falls back to simple search.
        """
        if not query or len(query.strip()) == 0:
            return []
        
        # Simple keyword-based search (fallback)
        results = self._keyword_search(query, topic, limit)
        
        return results
    
    def _keyword_search(
        self,
        query: str,
        topic: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Simple keyword-based search."""
        # Get verified sources
        sources = KnowledgeSource.objects.filter(verification_status='verified')
        
        # Filter by topic if specified
        if topic:
            sources = sources.filter(
                Q(title__icontains=topic) | Q(description__icontains=topic)
            )
        
        # Search in chunks
        query_words = query.lower().split()
        chunks = DocumentChunk.objects.filter(source__in=sources)
        
        # Score chunks by keyword matches
        scored_chunks = []
        for chunk in chunks:
            content_lower = chunk.content.lower()
            score = sum(1 for word in query_words if word in content_lower)
            
            if score > 0:
                scored_chunks.append({
                    'chunk': chunk,
                    'score': score,
                    'relevance': score / len(query_words)
                })
        
        # Sort by score
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Format results
        results = []
        for item in scored_chunks[:limit]:
            chunk = item['chunk']
            results.append({
                'chunk_id': chunk.id,
                'source_id': chunk.source.id,
                'source_title': chunk.source.title,
                'source_url': chunk.source.source_url,
                'content': chunk.content,
                'relevance_score': item['relevance'],
                'chunk_index': chunk.chunk_index
            })
        
        return results
    
    def get_context_for_question(
        self,
        topic: str,
        difficulty: str = 'intermediate',
        limit: int = 3
    ) -> str:
        """
        Get relevant context for generating interview questions.
        
        Returns formatted context string with citations.
        """
        # Search for relevant content
        results = self.search(topic, topic=topic, limit=limit)
        
        if not results:
            return f"No documentation available for {topic}."
        
        # Format context
        context_parts = [f"Relevant documentation for {topic}:\n"]
        
        for idx, result in enumerate(results, 1):
            context_parts.append(f"\n[Source {idx}: {result['source_title']}]")
            context_parts.append(result['content'][:300] + "...")
        
        return '\n'.join(context_parts)
    
    def verify_answer_with_sources(
        self,
        question: str,
        answer: str,
        topic: str
    ) -> Dict[str, Any]:
        """
        Verify if answer is supported by knowledge sources.
        
        Returns verification result with supporting/contradicting sources.
        """
        # Search for relevant content
        search_query = f"{question} {answer}"
        results = self.search(search_query, topic=topic, limit=5)
        
        if not results:
            return {
                'verified': False,
                'confidence': 0.0,
                'message': 'No sources available for verification',
                'sources': []
            }
        
        # Check if answer concepts appear in sources
        answer_words = set(answer.lower().split())
        
        supporting_sources = []
        for result in results:
            content_words = set(result['content'].lower().split())
            overlap = len(answer_words & content_words)
            
            if overlap / len(answer_words) > 0.3:  # 30% overlap threshold
                supporting_sources.append({
                    'title': result['source_title'],
                    'url': result['source_url'],
                    'relevance': result['relevance_score']
                })
        
        verified = len(supporting_sources) > 0
        confidence = len(supporting_sources) / len(results) if results else 0.0
        
        return {
            'verified': verified,
            'confidence': confidence,
            'message': f"Found {len(supporting_sources)} supporting sources" if verified else "Answer not supported by sources",
            'sources': supporting_sources
        }
    
    def get_source_list(self) -> List[Dict[str, Any]]:
        """Get list of all verified knowledge sources."""
        sources = KnowledgeSource.objects.filter(
            verification_status='verified'
        ).order_by('-import_date')
        
        return [{
            'id': source.id,
            'title': source.title,
            'url': source.source_url,
            'license': source.license_info,
            'version': source.version,
            'chunk_count': source.chunks.count(),
            'import_date': source.import_date.isoformat()
        } for source in sources]
