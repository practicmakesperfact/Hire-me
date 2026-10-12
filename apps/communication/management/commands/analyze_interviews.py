from django.core.management.base import BaseCommand
from apps.interviews.models import InterviewSession
from services.communication_analyzer.issue_detector import IssueDetector


class Command(BaseCommand):
    help = 'Analyze completed interviews for communication issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--session-id',
            type=int,
            help='Analyze specific session ID'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Analyze sessions for specific user (username)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Analyze all finished sessions'
        )
    
    def handle(self, *args, **options):
        detector = IssueDetector()
        
        # Get sessions to analyze
        sessions = InterviewSession.objects.filter(status='finished')
        
        if options['session_id']:
            sessions = sessions.filter(id=options['session_id'])
        elif options['user']:
            sessions = sessions.filter(user__username=options['user'])
        elif not options['all']:
            self.stdout.write(self.style.WARNING(
                'Use --session-id, --user, or --all to specify what to analyze'
            ))
            return
        
        if sessions.count() == 0:
            self.stdout.write('No finished sessions found')
            return
        
        self.stdout.write(f'Analyzing {sessions.count()} session(s)...\n')
        
        total_issues = 0
        for session in sessions:
            self.stdout.write(f'Session #{session.id} ({session.topic}) - {session.user.username}')
            
            result = detector.batch_analyze_session(session, save=True)
            stats = result['stats']
            
            self.stdout.write(f'  Analyzed {stats["analyzed_turns"]} turns')
            self.stdout.write(f'  Found {stats["total_issues"]} issues')
            
            if stats['issues_by_category']:
                self.stdout.write('  By category:')
                for cat, count in stats['issues_by_category'].items():
                    self.stdout.write(f'    - {cat}: {count}')
            
            total_issues += stats['total_issues']
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS(
            f'\nAnalysis complete! Found {total_issues} total issues across {sessions.count()} sessions'
        ))
