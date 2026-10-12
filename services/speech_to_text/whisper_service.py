import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from django.conf import settings
import subprocess

logger = logging.getLogger(__name__)


class WhisperService:
    """Local speech-to-text using faster-whisper."""
    
    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None
    ):
        self.model_size = model_size or getattr(settings, 'WHISPER_MODEL', 'base')
        self.device = device or getattr(settings, 'WHISPER_DEVICE', 'cpu')
        self._model = None
    
    def _load_model(self):
        """Lazy load the Whisper model."""
        if self._model is not None:
            return self._model
        
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8"  # Optimized for CPU
            )
            logger.info("Whisper model loaded successfully")
            return self._model
            
        except ImportError as e:
            logger.error(f"faster-whisper not installed: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        try:
            model = self._load_model()
            return model is not None
        except Exception:
            return False
    
    def transcribe_file(
        self,
        audio_path: str,
        language: Optional[str] = 'en'
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file to text.
        
        Returns:
            Dict with 'text', 'segments', 'language', 'confidence'
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        model = self._load_model()
        if model is None:
            logger.error("Whisper model not available")
            return None
        
        try:
            # Transcribe with word-level timestamps
            segments, info = model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                vad_filter=True,  # Voice activity detection
            )
            
            # Extract segments
            segment_list = []
            full_text = []
            total_confidence = 0
            segment_count = 0
            
            for segment in segments:
                segment_dict = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'confidence': getattr(segment, 'avg_logprob', 0)
                }
                
                segment_list.append(segment_dict)
                full_text.append(segment.text.strip())
                total_confidence += segment_dict['confidence']
                segment_count += 1
            
            avg_confidence = total_confidence / segment_count if segment_count > 0 else 0
            
            result = {
                'text': ' '.join(full_text),
                'segments': segment_list,
                'language': info.language,
                'confidence': avg_confidence,
                'duration': info.duration
            }
            
            logger.info(f"Transcribed: {result['text'][:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None
    
    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate audio file format, size, and duration.
        
        Returns:
            Dict with 'valid', 'errors', 'duration', 'size'
        """
        errors = []
        
        # Check existence
        if not os.path.exists(file_path):
            return {
                'valid': False,
                'errors': ['File does not exist'],
                'duration': None,
                'size': None
            }
        
        # Check size
        file_size = os.path.getsize(file_path)
        max_size = getattr(settings, 'MAX_AUDIO_FILE_SIZE_MB', 10) * 1024 * 1024
        
        if file_size > max_size:
            errors.append(f'File too large: {file_size / 1024 / 1024:.2f}MB (max: {max_size / 1024 / 1024}MB)')
        
        # Check duration using ffprobe
        duration = self._get_audio_duration(file_path)
        max_duration = getattr(settings, 'MAX_AUDIO_DURATION_SECONDS', 300)
        
        if duration and duration > max_duration:
            errors.append(f'Audio too long: {duration}s (max: {max_duration}s)')
        
        # Check format
        valid_extensions = ['.wav', '.mp3', '.ogg', '.flac', '.m4a']
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext not in valid_extensions:
            errors.append(f'Unsupported format: {file_ext}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'duration': duration,
            'size': file_size
        }
    
    def _get_audio_duration(self, file_path: str) -> Optional[float]:
        """Get audio duration using ffprobe."""
        try:
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    file_path
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            logger.warning(f"Could not get audio duration: {e}")
        
        return None
    
    def convert_audio(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        target_format: str = 'wav',
        sample_rate: int = 16000
    ) -> Optional[str]:
        """
        Convert audio to a format supported by Whisper using FFmpeg.
        
        Returns:
            Path to converted file or None if failed
        """
        if output_path is None:
            base = os.path.splitext(input_path)[0]
            output_path = f"{base}_converted.{target_format}"
        
        try:
            subprocess.run(
                [
                    'ffmpeg',
                    '-i', input_path,
                    '-ar', str(sample_rate),
                    '-ac', '1',  # Mono
                    '-y',  # Overwrite
                    output_path
                ],
                capture_output=True,
                timeout=30,
                check=True
            )
            
            logger.info(f"Converted audio: {output_path}")
            return output_path
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Audio conversion failed: {e}")
            return None


# Singleton instance
_whisper_service: Optional[WhisperService] = None


def get_whisper_service() -> WhisperService:
    """Get or create WhisperService singleton."""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService()
    return _whisper_service
