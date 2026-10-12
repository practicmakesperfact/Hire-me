from django.core.management.base import BaseCommand
from apps.interviews.models import Role, Topic
from apps.questions.models import Question


class Command(BaseCommand):
    help = 'Seed initial data for roles, topics, and questions'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding roles...')
        roles_data = [
            {'name': 'Software Engineer', 'description': 'Full-stack or backend development'},
            {'name': 'Frontend Developer', 'description': 'UI/UX and React development'},
            {'name': 'Data Scientist', 'description': 'Machine learning and analytics'},
            {'name': 'DevOps Engineer', 'description': 'Infrastructure and automation'},
            {'name': 'Product Manager', 'description': 'Product strategy and management'},
        ]
        
        for role_data in roles_data:
            Role.objects.get_or_create(name=role_data['name'], defaults=role_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(roles_data)} roles'))
        
        self.stdout.write('Seeding topics...')
        topics_data = [
            {'name': 'Python', 'description': 'Python programming', 'difficulty_level': 'intermediate'},
            {'name': 'Django', 'description': 'Django web framework', 'difficulty_level': 'intermediate'},
            {'name': 'React', 'description': 'React frontend library', 'difficulty_level': 'intermediate'},
            {'name': 'JavaScript', 'description': 'JavaScript programming', 'difficulty_level': 'beginner'},
            {'name': 'SQL', 'description': 'Database queries', 'difficulty_level': 'beginner'},
            {'name': 'Data Structures', 'description': 'Algorithms and data structures', 'difficulty_level': 'advanced'},
            {'name': 'Machine Learning', 'description': 'ML algorithms', 'difficulty_level': 'advanced'},
            {'name': 'System Design', 'description': 'Architecture and scaling', 'difficulty_level': 'advanced'},
            {'name': 'Behavioral', 'description': 'Behavioral questions', 'difficulty_level': 'intermediate'},
        ]
        
        for topic_data in topics_data:
            Topic.objects.get_or_create(name=topic_data['name'], defaults=topic_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(topics_data)} topics'))
        
        self.stdout.write('Seeding questions...')
        python_topic = Topic.objects.get(name='Python')
        django_topic = Topic.objects.get(name='Django')
        behavioral_topic = Topic.objects.get(name='Behavioral')
        
        questions_data = [
            {
                'topic': python_topic,
                'question_text': 'What is a Python decorator and how do you use it?',
                'difficulty': 'intermediate',
                'question_type': 'technical',
                'expected_answer': 'A decorator is a function that wraps another function to modify its behavior',
                'key_points': 'Functions as first-class objects, @ syntax, common use cases'
            },
            {
                'topic': python_topic,
                'question_text': 'Explain the difference between lists and tuples in Python.',
                'difficulty': 'beginner',
                'question_type': 'technical',
                'expected_answer': 'Lists are mutable, tuples are immutable',
                'key_points': 'Mutability, performance, use cases'
            },
            {
                'topic': django_topic,
                'question_text': 'What is the Django ORM and why is it useful?',
                'difficulty': 'intermediate',
                'question_type': 'technical',
                'expected_answer': 'Object-Relational Mapper that allows database queries using Python code',
                'key_points': 'Abstraction, security, portability'
            },
            {
                'topic': django_topic,
                'question_text': 'How does Django handle database migrations?',
                'difficulty': 'intermediate',
                'question_type': 'technical',
                'expected_answer': 'Using migration files that track schema changes',
                'key_points': 'makemigrations, migrate, version control'
            },
            {
                'topic': behavioral_topic,
                'question_text': 'Tell me about a challenging project you worked on.',
                'difficulty': 'intermediate',
                'question_type': 'behavioral',
                'expected_answer': 'STAR method response',
                'key_points': 'Situation, Task, Action, Result'
            },
            {
                'topic': behavioral_topic,
                'question_text': 'How do you handle disagreements with team members?',
                'difficulty': 'intermediate',
                'question_type': 'behavioral',
                'expected_answer': 'Focus on communication and finding common ground',
                'key_points': 'Active listening, compromise, professionalism'
            },
        ]
        
        for question_data in questions_data:
            Question.objects.get_or_create(
                topic=question_data['topic'],
                question_text=question_data['question_text'],
                defaults=question_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(questions_data)} questions'))
        self.stdout.write(self.style.SUCCESS('Data seeding complete!'))
