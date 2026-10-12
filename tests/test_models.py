import pytest
from apps.interviews.models import Role, Topic, InterviewSession
from apps.questions.models import Question
from apps.knowledge.models import KnowledgeSource, DocumentChunk
from apps.communication.models import CommunicationIssue
from apps.practice.models import PracticeAttempt, ProgressSnapshot
from datetime import date


@pytest.mark.django_db
class TestModels:
    
    def test_create_role(self):
        role = Role.objects.create(
            name='Software Engineer',
            description='Backend development role'
        )
        assert str(role) == 'Software Engineer'
        assert Role.objects.count() == 1
    
    def test_create_topic(self):
        topic = Topic.objects.create(
            name='Python',
            description='Python programming',
            difficulty_level='intermediate'
        )
        assert str(topic) == 'Python'
        assert topic.difficulty_level == 'intermediate'
    
    def test_create_interview_session(self, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Django')
        
        session = InterviewSession.objects.create(
            user=user,
            role=role,
            topic=topic,
            status='ready'
        )
        assert session.status == 'ready'
        assert session.user == user
    
    def test_create_question(self):
        topic = Topic.objects.create(name='Python')
        question = Question.objects.create(
            topic=topic,
            question_text='What is a decorator?',
            difficulty='intermediate'
        )
        assert 'What is a decorator?' in str(question)
    
    def test_create_knowledge_source(self):
        source = KnowledgeSource.objects.create(
            title='Python Docs',
            source_url='https://docs.python.org',
            content_hash='abc123'
        )
        assert str(source) == 'Python Docs'
    
    def test_create_communication_issue(self, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Django')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user,
            session=session,
            category='grammar',
            original_text='I goes to the store',
            proposed_correction='I go to the store',
            status='needs_review'
        )
        assert issue.category == 'grammar'
        assert issue.status == 'needs_review'
    
    def test_create_progress_snapshot(self, user):
        snapshot = ProgressSnapshot.objects.create(
            user=user,
            snapshot_date=date.today(),
            total_issues=10,
            mastered_issues=5
        )
        assert snapshot.total_issues == 10
        assert snapshot.mastered_issues == 5
