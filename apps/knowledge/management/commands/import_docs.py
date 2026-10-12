from django.core.management.base import BaseCommand
from services.rag.document_processor import DocumentProcessor
from pathlib import Path


class Command(BaseCommand):
    help = 'Import documentation files into knowledge base'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to file to import'
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Title for the document'
        )
        parser.add_argument(
            '--url',
            type=str,
            default='',
            help='Source URL'
        )
        parser.add_argument(
            '--license',
            type=str,
            default='',
            help='License information'
        )
        parser.add_argument(
            '--version',
            type=str,
            default='',
            help='Document version'
        )
    
    def handle(self, *args, **options):
        file_path = options.get('file')
        title = options.get('title')
        
        if not file_path or not title:
            self.stdout.write(self.style.ERROR(
                'Both --file and --title are required'
            ))
            return
        
        if not Path(file_path).exists():
            self.stdout.write(self.style.ERROR(
                f'File not found: {file_path}'
            ))
            return
        
        self.stdout.write(f'Importing {file_path}...')
        
        processor = DocumentProcessor()
        source = processor.import_text_file(
            file_path=file_path,
            title=title,
            source_url=options.get('url', ''),
            license_info=options.get('license', ''),
            version=options.get('version', '')
        )
        
        if source:
            stats = processor.get_source_stats(source)
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ Successfully imported: {title}'
            ))
            self.stdout.write(f'  Source ID: {source.id}')
            self.stdout.write(f'  Chunks: {stats["chunk_count"]}')
            self.stdout.write(f'  Total words: {stats["total_words"]}')
            self.stdout.write(f'  Avg chunk size: {stats["avg_chunk_size"]} words')
        else:
            self.stdout.write(self.style.ERROR('Import failed'))
