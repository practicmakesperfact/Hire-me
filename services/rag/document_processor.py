import logging
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from apps.knowledge.models import KnowledgeSource, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process and chunk documents for RAG."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def import_text_file(
        self,
        file_path: str,
        title: str,
        source_url: str = '',
        license_info: str = '',
        version: str = '',
        description: str = ''
    ) -> Optional[KnowledgeSource]:
        """Import a text file as a knowledge source."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Calculate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check if already imported
            if KnowledgeSource.objects.filter(content_hash=content_hash).exists():
                logger.info(f"Document already imported: {title}")
                return KnowledgeSource.objects.get(content_hash=content_hash)
            
            # Create knowledge source
            source = KnowledgeSource.objects.create(
                title=title,
                source_url=source_url,
                license_info=license_info,
                version=version,
                description=description,
                content_hash=content_hash,
                verification_status='verified'
            )
            
            # Chunk and store
            chunks = self._chunk_text(content)
            self._save_chunks(source, chunks)
            
            logger.info(f"Imported {title}: {len(chunks)} chunks")
            return source
            
        except Exception as e:
            logger.error(f"Failed to import document: {e}")
            return None
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            # Get chunk
            chunk_words = words[i:i + self.chunk_size]
            chunk = ' '.join(chunk_words)
            chunks.append(chunk)
            
            # Move forward with overlap
            i += self.chunk_size - self.chunk_overlap
            
            if i >= len(words):
                break
        
        return chunks
    
    def _save_chunks(self, source: KnowledgeSource, chunks: List[str]):
        """Save chunks to database."""
        chunk_objects = []
        
        for idx, content in enumerate(chunks):
            chunk_hash = hashlib.sha256(content.encode()).hexdigest()
            
            chunk_objects.append(DocumentChunk(
                source=source,
                chunk_index=idx,
                content=content,
                chunk_hash=chunk_hash
            ))
        
        DocumentChunk.objects.bulk_create(chunk_objects)
    
    def import_markdown(
        self,
        file_path: str,
        title: str,
        **kwargs
    ) -> Optional[KnowledgeSource]:
        """Import markdown file with basic parsing."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic markdown processing - could be enhanced
            # Remove markdown headers but keep content
            import re
            content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
            
            return self.import_text_file(file_path, title, **kwargs)
            
        except Exception as e:
            logger.error(f"Failed to import markdown: {e}")
            return None
    
    def delete_source(self, source_id: int) -> bool:
        """Delete a knowledge source and its chunks."""
        try:
            source = KnowledgeSource.objects.get(id=source_id)
            source.delete()  # Cascades to chunks
            logger.info(f"Deleted source: {source.title}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete source: {e}")
            return False
    
    def get_source_stats(self, source: KnowledgeSource) -> Dict[str, Any]:
        """Get statistics for a knowledge source."""
        chunks = source.chunks.all()
        
        total_words = sum(len(chunk.content.split()) for chunk in chunks)
        
        return {
            'source_id': source.id,
            'title': source.title,
            'chunk_count': chunks.count(),
            'total_words': total_words,
            'avg_chunk_size': total_words // chunks.count() if chunks.count() > 0 else 0,
            'verification_status': source.verification_status
        }
