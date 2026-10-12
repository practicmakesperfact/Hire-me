from django.core.management.base import BaseCommand
from services.llm.ollama_client import get_ollama_client


class Command(BaseCommand):
    help = 'Check Ollama service status and available models'
    
    def handle(self, *args, **kwargs):
        ollama = get_ollama_client()
        
        self.stdout.write('Checking Ollama service...')
        
        if ollama.is_available():
            self.stdout.write(self.style.SUCCESS('✓ Ollama is available'))
            
            self.stdout.write(f'\nBase URL: {ollama.base_url}')
            self.stdout.write(f'Model: {ollama.model}')
            self.stdout.write(f'Timeout: {ollama.timeout}s')
            
            self.stdout.write('\nAvailable models:')
            models = ollama.list_models()
            
            if models:
                for model in models:
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0) / (1024**3)  # Convert to GB
                    self.stdout.write(f'  - {name} ({size:.2f} GB)')
            else:
                self.stdout.write('  No models found')
            
            # Test generation
            self.stdout.write('\nTesting generation...')
            response = ollama.generate(
                prompt="Say 'Hello, Ollama is working!' and nothing else.",
                temperature=0.1
            )
            
            if response:
                self.stdout.write(self.style.SUCCESS(f'✓ Generation test: {response}'))
            else:
                self.stdout.write(self.style.ERROR('✗ Generation test failed'))
        else:
            self.stdout.write(self.style.ERROR('✗ Ollama is not available'))
            self.stdout.write('\nMake sure Ollama is installed and running:')
            self.stdout.write('  1. Download from: https://ollama.ai/')
            self.stdout.write('  2. Run: ollama serve')
            self.stdout.write(f'  3. Pull model: ollama pull {ollama.model}')
