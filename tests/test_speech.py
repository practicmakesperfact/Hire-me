import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from services.speech_to_text.whisper_service import WhisperService
from services.text_to_speech.piper_service import PiperService


@pytest.mark.django_db
class TestSpeechToText:
    
    def test_whisper_service_initialization(self):
        service = WhisperService()
        assert service.model_size in ['tiny', 'base', 'small', 'medium', 'large']
        assert service.device in ['cpu', 'cuda']
    
    @patch('services.speech_to_text.whisper_service.WhisperModel')
    def test_whisper_is_available(self, mock_model):
        mock_model.return_value = MagicMock()
        
        service = WhisperService()
        result = service.is_available()
        
        assert result is True
    
    def test_validate_audio_file_not_exists(self):
        service = WhisperService()
        result = service.validate_audio_file('nonexistent.wav')
        
        assert result['valid'] is False
        assert 'does not exist' in result['errors'][0]
    
    @patch('subprocess.run')
    def test_get_audio_duration(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '10.5'
        
        service = WhisperService()
        duration = service._get_audio_duration('test.wav')
        
        assert duration == 10.5


@pytest.mark.django_db
class TestTextToSpeech:
    
    @patch('subprocess.run')
    def test_piper_is_available(self, mock_run):
        mock_run.return_value.returncode = 0
        
        service = PiperService()
        assert service.is_available() is True
    
    @patch('subprocess.run')
    def test_piper_not_available(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        
        service = PiperService()
        assert service.is_available() is False
    
    def test_synthesize_empty_text(self):
        service = PiperService()
        result = service.synthesize('')
        
        assert result is None
    
    @patch('subprocess.run')
    @patch('os.path.exists')
    def test_synthesize_success(self, mock_exists, mock_run):
        mock_run.return_value.returncode = 0
        mock_exists.return_value = True
        
        service = PiperService()
        result = service.synthesize('Hello world')
        
        assert result is not None
    
    @patch('subprocess.run')
    def test_synthesize_cached(self, mock_run):
        service = PiperService()
        
        # Mock cache exists
        with patch('os.path.exists', return_value=True):
            result = service.synthesize('Hello', cache=True)
            
            # Should not call piper if cached
            mock_run.assert_not_called()


@pytest.mark.django_db
class TestSpeechAPI:
    
    def test_transcribe_no_file(self, authenticated_client):
        url = reverse('speech-transcribe')
        response = authenticated_client.post(url)
        
        assert response.status_code == 400
        assert 'error' in response.json()
    
    @patch('services.speech_to_text.whisper_service.WhisperService.validate_audio_file')
    @patch('services.speech_to_text.whisper_service.WhisperService.transcribe_file')
    def test_transcribe_success(self, mock_transcribe, mock_validate, authenticated_client):
        mock_validate.return_value = {
            'valid': True,
            'errors': [],
            'duration': 10.0,
            'size': 1024
        }
        mock_transcribe.return_value = {
            'text': 'Hello world',
            'language': 'en',
            'confidence': 0.95,
            'duration': 10.0,
            'segments': []
        }
        
        url = reverse('speech-transcribe')
        audio_file = SimpleUploadedFile('test.wav', b'fake audio content', content_type='audio/wav')
        
        response = authenticated_client.post(url, {'audio': audio_file})
        
        assert response.status_code == 200
        assert response.json()['text'] == 'Hello world'
    
    def test_synthesize_no_text(self, authenticated_client):
        url = reverse('speech-synthesize')
        response = authenticated_client.post(url, {})
        
        assert response.status_code == 400
    
    def test_synthesize_text_too_long(self, authenticated_client):
        url = reverse('speech-synthesize')
        long_text = 'a' * 1001
        response = authenticated_client.post(url, {'text': long_text}, content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('services.text_to_speech.piper_service.PiperService.is_available')
    @patch('services.text_to_speech.piper_service.PiperService.synthesize')
    def test_synthesize_success(self, mock_synth, mock_available, authenticated_client):
        mock_available.return_value = True
        mock_synth.return_value = '/media/audio/tts/test.wav'
        
        url = reverse('speech-synthesize')
        response = authenticated_client.post(url, {'text': 'Hello'}, content_type='application/json')
        
        assert response.status_code == 200
        assert 'audio_url' in response.json()
    
    def test_analyze_no_file(self, authenticated_client):
        url = reverse('speech-analyze')
        response = authenticated_client.post(url)
        
        assert response.status_code == 400
