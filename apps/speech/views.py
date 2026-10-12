from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
from services.speech_to_text.whisper_service import get_whisper_service
from services.text_to_speech.piper_service import get_piper_service


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def transcribe_view(request):
    """Transcribe uploaded audio file."""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    language = request.data.get('language', 'en')
    
    # Save temporarily
    temp_path = default_storage.save(f'temp/{audio_file.name}', audio_file)
    full_path = os.path.join(default_storage.location, temp_path)
    
    try:
        whisper = get_whisper_service()
        
        # Validate audio
        validation = whisper.validate_audio_file(full_path)
        if not validation['valid']:
            return Response(
                {'error': 'Invalid audio file', 'details': validation['errors']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Transcribe
        result = whisper.transcribe_file(full_path, language)
        
        if result:
            return Response({
                'text': result['text'],
                'language': result['language'],
                'confidence': result['confidence'],
                'duration': result['duration'],
                'segments': result['segments']
            })
        else:
            return Response(
                {'error': 'Transcription failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    finally:
        # Clean up temp file
        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def synthesize_view(request):
    """Convert text to speech."""
    text = request.data.get('text')
    
    if not text:
        return Response(
            {'error': 'No text provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(text) > 1000:
        return Response(
            {'error': 'Text too long (max 1000 characters)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    piper = get_piper_service()
    
    if not piper.is_available():
        return Response(
            {'error': 'TTS service not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    audio_path = piper.synthesize(text)
    
    if audio_path:
        # Return relative path
        relative_path = os.path.relpath(audio_path, default_storage.location)
        return Response({
            'audio_url': default_storage.url(relative_path),
            'text': text
        })
    else:
        return Response(
            {'error': 'Speech synthesis failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_view(request):
    """Analyze audio file for speech metrics."""
    if 'audio' not in request.FILES:
        return Response(
            {'error': 'No audio file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = request.FILES['audio']
    
    # Save temporarily
    temp_path = default_storage.save(f'temp/{audio_file.name}', audio_file)
    full_path = os.path.join(default_storage.location, temp_path)
    
    try:
        # Basic analysis placeholder - can be extended with librosa
        whisper = get_whisper_service()
        validation = whisper.validate_audio_file(full_path)
        
        if validation['valid']:
            return Response({
                'duration': validation['duration'],
                'size': validation['size'],
                'format': os.path.splitext(audio_file.name)[1],
                'valid': True
            })
        else:
            return Response(
                {'error': 'Invalid audio file', 'details': validation['errors']},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    finally:
        # Clean up
        if default_storage.exists(temp_path):
            default_storage.delete(temp_path)
