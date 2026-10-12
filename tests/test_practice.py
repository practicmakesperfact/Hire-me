import pytest
from django.urls import reverse
from apps.interviews.models import Role, Topic, InterviewSession
from apps.communication.models import CommunicationIssue
from apps.practice.models import PracticeAttempt


@pytest.mark.django_db
class TestPracticeQueue:
    
    def test_practice_queue_empty(self, authenticated_client):
        url = reverse('practice-queue')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['count'] == 0
    
    def test_practice_queue_with_issues(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        # Create confirmed issues
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='I goes', proposed_correction='I go',
            status='confirmed'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='pronunciation',
            original_text='Test', status='confirmed'
        )
        
        url = reverse('practice-queue')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['count'] == 2
    
    def test_practice_queue_filters_by_category(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 1', status='confirmed'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='pronunciation',
            original_text='Test 2', status='confirmed'
        )
        
        url = reverse('practice-queue') + '?category=grammar'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json()['count'] == 1
    
    def test_practice_queue_excludes_needs_review(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test', status='needs_review'
        )
        
        url = reverse('practice-queue')
        response = authenticated_client.get(url)
        
        assert response.json()['count'] == 0


@pytest.mark.django_db
class TestPracticeSubmit:
    
    def test_submit_text_practice(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='I goes', proposed_correction='I go',
            status='confirmed'
        )
        
        url = reverse('practice-submit')
        response = authenticated_client.post(url, {
            'issue_id': issue.id,
            'attempt_text': 'I go'
        }, content_type='application/json')
        
        assert response.status_code == 201
        assert PracticeAttempt.objects.filter(issue=issue).count() == 1
        
        issue.refresh_from_db()
        assert issue.practice_count == 1
        assert issue.status == 'practicing'
    
    def test_submit_perfect_attempt(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='I goes', proposed_correction='I go',
            status='confirmed'
        )
        
        url = reverse('practice-submit')
        response = authenticated_client.post(url, {
            'issue_id': issue.id,
            'attempt_text': 'I go'
        }, content_type='application/json')
        
        assert response.status_code == 201
        assert response.json()['score'] == 10.0
        assert 'Perfect' in response.json()['feedback']
    
    def test_auto_master_after_three_good_attempts(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='I goes', proposed_correction='I go',
            status='confirmed'
        )
        
        url = reverse('practice-submit')
        
        # Submit 3 good attempts
        for _ in range(3):
            authenticated_client.post(url, {
                'issue_id': issue.id,
                'attempt_text': 'I go'
            }, content_type='application/json')
        
        issue.refresh_from_db()
        assert issue.status == 'mastered'


@pytest.mark.django_db
class TestPracticeProgress:
    
    def test_progress_view(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        # Create issues in different states
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 1', status='confirmed'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 2', status='practicing'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 3', status='mastered'
        )
        
        url = reverse('practice-progress')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert data['issues']['total'] == 3
        assert data['issues']['confirmed'] == 1
        assert data['issues']['practicing'] == 1
        assert data['issues']['mastered'] == 1
        assert data['completion_rate'] == 33.3


@pytest.mark.django_db
class TestMarkMastered:
    
    def test_mark_issue_mastered(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test', status='practicing'
        )
        
        url = reverse('practice-mark-mastered', kwargs={'issue_id': issue.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        issue.refresh_from_db()
        assert issue.status == 'mastered'


@pytest.mark.django_db
class TestPracticeHistory:
    
    def test_practice_history(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test', status='confirmed'
        )
        
        PracticeAttempt.objects.create(
            user=user, issue=issue,
            attempt_text='Attempt 1',
            score=8.0
        )
        PracticeAttempt.objects.create(
            user=user, issue=issue,
            attempt_text='Attempt 2',
            score=9.0
        )
        
        url = reverse('practice-history')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()) == 2
    
    def test_practice_history_filter_by_issue(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue1 = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 1', status='confirmed'
        )
        issue2 = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 2', status='confirmed'
        )
        
        PracticeAttempt.objects.create(user=user, issue=issue1, attempt_text='A1')
        PracticeAttempt.objects.create(user=user, issue=issue2, attempt_text='A2')
        
        url = reverse('practice-history') + f'?issue_id={issue1.id}'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()) == 1
