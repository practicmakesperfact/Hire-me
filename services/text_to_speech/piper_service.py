import logging
import os
import subprocess
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class PiperService:
    """Local text-to-speech using Piper."""
    
    def __init__(
        self,
        voice: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        self.voice = voice or getattr(settings, 'TTS_VOICE', 'en_US-lessac-medium')
        self.output_dir = output_dir or os.path.join(settings.MEDIA_ROOT, 'audio', 'tts')
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def is_available(self) -> bool:
        """Check if Piper is available."""
        try:
            result = subprocess.run(
                ['piper', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.warning("Piper not available")
            return False
    
    def synthesize(
        self,
        text: str,
        output_path: Optional[str] = None,
        cache: bool = True
    ) -> Optional[str]:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            output_path: Custom output path (optional)
            cache: Whether to use cached audio for same text
        
        Returns:
            Path to generated audio file or None if failed
        """
        if not text or len(text.strip()) == 0:
            logger.error("Empty text provided")
            return None
        
        # Generate output path if not provided
        if output_path is None:
            # Use hash of text for caching
            text_hash = hashlib.md5(text.encode()).hexdigest()
            output_path = os.path.join(self.output_dir, f"{text_hash}.wav")
        
        # Return cached file if exists
        if cache and os.path.exists(output_path):
            logger.info(f"Using cached TTS: {output_path}")
            return output_path
        
        try:
            # Run Piper
            process = subprocess.run(
                ['piper', '--model', self.voice, '--output_file', output_path],
                input=text.encode('utf-8'),
                capture_output=True,
                timeout=30
            )
            
            if process.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Generated TTS: {output_path}")
                return output_path
            else:
                logger.error(f"Piper failed: {process.stderr.decode()}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("TTS generation timed out")
            return None
        except FileNotFoundError:
            logger.error("Piper not found. Install from: https://github.com/rhasspy/piper")
            return None
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return None
    
    def synthesize_with_fallback(
        self,
        text: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize with fallback and status info.
        
        Returns:
            Dict with 'success', 'audio_path', 'error'
        """
        audio_path = self.synthesize(text, output_path)
        
        if audio_path:
            return {
                'success': True,
                'audio_path': audio_path,
                'error': None
            }
        else:
            return {
                'success': False,
                'audio_path': None,
                'error': 'TTS service unavailable'
            }
    
    def clear_cache(self) -> int:
        """
        Clear cached TTS files.
        
        Returns:
            Number of files deleted
        """
        count = 0
        try:
            for file in Path(self.output_dir).glob('*.wav'):
                file.unlink()
                count += 1
            logger.info(f"Cleared {count} cached TTS files")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
        
        return count


# Singleton instance
_piper_service: Optional[PiperService] = None


def get_piper_service() -> PiperService:
    """Get or create PiperService singleton."""
    global _piper_service
    if _piper_service is None:
        _piper_service = PiperService()
    return _piper_service
