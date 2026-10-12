"""
Phase 4 API test script - Speech Processing
Run after: python manage.py runserver
Requires: faster-whisper, piper-tts, FFmpeg installed
"""
import requests
import os

BASE_URL = "http://localhost:8000/api/v1"
session = requests.Session()


def login():
    """Login and return session."""
    response = session.post(f"{BASE_URL}/auth/login/", json={
        "username": "testuser",
        "password": "testpass123"
    })
    print(f"Login: {response.status_code}")
    return response.ok


def test_text_to_speech():
    """Test text-to-speech endpoint."""
    print("\n=== Testing Text-to-Speech ===")
    
    response = session.post(
        f"{BASE_URL}/speech/synthesize/",
        json={"text": "Hello, this is a test of the text to speech system."}
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"Audio URL: {data.get('audio_url')}")
        print(f"Text: {data.get('text')}")
    else:
        print(f"Error: {response.text}")
        print("\nNote: Make sure Piper is installed:")
        print("  pip install piper-tts")


def test_speech_to_text():
    """Test speech-to-text endpoint."""
    print("\n=== Testing Speech-to-Text ===")
    
    # Create a simple WAV file for testing (would need actual audio in production)
    print("Note: This test requires an actual audio file")
    print("To test manually:")
    print("  curl -X POST http://localhost:8000/api/v1/speech/transcribe/")
    print("       -H 'Authorization: Session' -F 'audio=@/path/to/audio.wav'")
    
    # Check if we have a test audio file
    test_audio = 'test_audio.wav'
    if os.path.exists(test_audio):
        with open(test_audio, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = session.post(f"{BASE_URL}/speech/transcribe/", files=files)
            
            print(f"Status: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"Transcribed Text: {data.get('text')}")
                print(f"Language: {data.get('language')}")
                print(f"Confidence: {data.get('confidence')}")
                print(f"Duration: {data.get('duration')}s")
            else:
                print(f"Error: {response.text}")
    else:
        print("No test audio file found. Create 'test_audio.wav' to test.")


def test_audio_analysis():
    """Test audio analysis endpoint."""
    print("\n=== Testing Audio Analysis ===")
    
    test_audio = 'test_audio.wav'
    if os.path.exists(test_audio):
        with open(test_audio, 'rb') as f:
            files = {'audio': ('test.wav', f, 'audio/wav')}
            response = session.post(f"{BASE_URL}/speech/analyze/", files=files)
            
            print(f"Status: {response.status_code}")
            if response.ok:
                data = response.json()
                print(f"Duration: {data.get('duration')}s")
                print(f"Size: {data.get('size')} bytes")
                print(f"Format: {data.get('format')}")
            else:
                print(f"Error: {response.text}")
    else:
        print("No test audio file found. Create 'test_audio.wav' to test.")


if __name__ == "__main__":
    print("=== Phase 4 Speech Processing Testing ===")
    print("\nPrerequisites:")
    print("  - faster-whisper: pip install faster-whisper")
    print("  - Piper TTS: pip install piper-tts")
    print("  - FFmpeg installed and in PATH")
    print("  - Check status: python manage.py check_speech")
    print()
    
    if not login():
        print("\nLogin failed! Create test user first.")
        exit(1)
    
    # Test TTS (doesn't require audio file)
    test_text_to_speech()
    
    # Test STT (requires audio file)
    test_speech_to_text()
    
    # Test analysis
    test_audio_analysis()
    
    print("\n=== Phase 4 Tests Complete ===")
    print("\nNote: Speech-to-text tests require actual audio files.")
    print("For full testing, provide test_audio.wav file.")
