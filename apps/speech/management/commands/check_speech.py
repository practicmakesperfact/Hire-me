from django.core.management.base import BaseCommand
from services.speech_to_text.whisper_service import get_whisper_service
from services.text_to_speech.piper_service import get_piper_service


class Command(BaseCommand):
    help = 'Check speech services (Whisper STT and Piper TTS) status'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('=== Checking Speech Services ===\n')
        
        # Check Whisper
        self.stdout.write('1. Checking Whisper (Speech-to-Text)...')
        whisper = get_whisper_service()
        
        if whisper.is_available():
            self.stdout.write(self.style.SUCCESS('✓ Whisper is available'))
            self.stdout.write(f'   Model: {whisper.model_size}')
            self.stdout.write(f'   Device: {whisper.device}')
        else:
            self.stdout.write(self.style.ERROR('✗ Whisper not available'))
            self.stdout.write('   Install: pip install faster-whisper')
        
        # Check Piper
        self.stdout.write('\n2. Checking Piper (Text-to-Speech)...')
        piper = get_piper_service()
        
        if piper.is_available():
            self.stdout.write(self.style.SUCCESS('✓ Piper is available'))
            self.stdout.write(f'   Voice: {piper.voice}')
            self.stdout.write(f'   Output dir: {piper.output_dir}')
            
            # Test synthesis
            self.stdout.write('\n   Testing TTS...')
            test_path = piper.synthesize('Hello, this is a test.')
            if test_path:
                self.stdout.write(self.style.SUCCESS(f'   ✓ Test synthesis: {test_path}'))
            else:
                self.stdout.write(self.style.ERROR('   ✗ Test synthesis failed'))
        else:
            self.stdout.write(self.style.ERROR('✗ Piper not available'))
            self.stdout.write('   Install from: https://github.com/rhasspy/piper')
        
        # Check FFmpeg
        self.stdout.write('\n3. Checking FFmpeg...')
        import subprocess
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS('✓ FFmpeg is available'))
            else:
                self.stdout.write(self.style.ERROR('✗ FFmpeg not available'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('✗ FFmpeg not found'))
            self.stdout.write('   Install from: https://ffmpeg.org/download.html')
        
        self.stdout.write('\n=== Check Complete ===')
