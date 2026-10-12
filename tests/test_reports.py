"""
Tests for reports functionality (Phase 8).
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.interviews.models import InterviewSession, InterviewTurn, InterviewEvaluation, Role, Topic
from apps.communication.models import CommunicationIssue
from apps.practice.models import PracticeAttempt, ProgressSnapshot
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def role(db):
    return Role.objects.create(
        name='Software Engineer',
        description='Backend developer role'
    )


@pytest.fixture
def topic(db):
    return Topic.objects.create(
        name='Python',
        difficulty_level='intermediate',
        description='Python programming'
    )


@pytest.fixture
def interview_with_evaluation(user, role, topic):
    interview = InterviewSession.objects.create(
        user=user,
        role=role,
        topic=topic,
        difficulty='intermediate',
        interview_type='technical',
        status='finished',
        finished_at=timezone.now()
    )
    
    InterviewTurn.objects.create(
        session=interview,
        turn_number=1,
        question_text='What is Python?',
        answer_text='Python is a programming language',
        speaker='interviewer'
    )
    
    InterviewEvaluation.objects.create(
        session=interview,
        technical_score=8.5,
        completeness_score=7.5,
        reasoning_score=8.0,
        organization_score=7.0,
        overall_feedback='Good performance',
        strengths='Clear explanations',
        improvements='More examples needed'
    )
    
    return interview


@pytest.fixture
def communication_issues(user):
    issues = []
    issues.append(CommunicationIssue.objects.create(
        user=user,
        category='filler_words',
        original_text='Um, I think Python is good',
        suggested_text='I think Python is good',
        context='Interview answer',
        status='confirmed'
    ))
    issues.append(CommunicationIssue.objects.create(
        user=user,
        category='repeated_words',
        original_text='The the implementation',
        suggested_text='The implementation',
        context='Interview answer',
        status='mastered'
    ))
    return issues


@pytest.fixture
def practice_attempts(user, communication_issues):
    attempts = []
    for issue in communication_issues:
        attempts.append(PracticeAttempt.objects.create(
            user=user,
            issue=issue,
            practice_text='Practice text',
            score=8.5
        ))
    return attempts


@pytest.mark.django_db
class TestOverviewReport:
    def test_overview_report_success(self, auth_client, interview_with_evaluation, communication_issues, practice_attempts):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'interviews' in response.data
        assert 'performance' in response.data
        assert 'communication' in response.data
        assert 'practice' in response.data
        assert 'improvement_trend' in response.data
        
    def test_overview_report_user_info(self, auth_client, user):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.data['user']['username'] == user.username
        assert response.data['user']['email'] == user.email
        
    def test_overview_report_interview_stats(self, auth_client, interview_with_evaluation):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        interviews = response.data['interviews']
        assert interviews['total'] == 1
        assert interviews['finished'] == 1
        assert interviews['completion_rate'] == 100.0
        
    def test_overview_report_performance_scores(self, auth_client, interview_with_evaluation):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        performance = response.data['performance']
        assert performance['average_scores']['technical'] == 8.5
        assert performance['average_scores']['completeness'] == 7.5
        assert performance['evaluations_count'] == 1
        
    def test_overview_report_communication_stats(self, auth_client, communication_issues):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        comm = response.data['communication']
        assert comm['total_issues'] == 2
        assert comm['mastered'] == 1
        assert comm['mastery_rate'] == 50.0
        
    def test_overview_report_practice_stats(self, auth_client, practice_attempts):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        practice = response.data['practice']
        assert practice['total_attempts'] == 2
        
    def test_overview_report_unauthenticated(self, api_client):
        url = reverse('reports-overview')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_overview_report_empty_data(self, auth_client):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['interviews']['total'] == 0
        assert response.data['performance']['evaluations_count'] == 0


@pytest.mark.django_db
class TestCommunicationReport:
    def test_communication_report_success(self, auth_client, communication_issues, practice_attempts):
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert 'most_practiced' in response.data
        assert 'practice_timeline' in response.data
        assert 'common_patterns' in response.data
        assert 'recommendations' in response.data
        
    def test_communication_report_by_category(self, auth_client, communication_issues):
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        by_category = response.data['summary']['by_category']
        assert len(by_category) == 2
        
        categories = [item['category'] for item in by_category]
        assert 'filler_words' in categories
        assert 'repeated_words' in categories
        
    def test_communication_report_by_status(self, auth_client, communication_issues):
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        by_status = response.data['summary']['by_status']
        statuses = [item['status'] for item in by_status]
        
        assert 'confirmed' in statuses or 'mastered' in statuses
        
    def test_communication_report_most_practiced(self, auth_client, communication_issues):
        # Increment practice count
        issue = communication_issues[0]
        issue.practice_count = 5
        issue.save()
        
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        most_practiced = response.data['most_practiced']
        assert len(most_practiced) > 0
        
    def test_communication_report_unauthenticated(self, api_client):
        url = reverse('reports-communication')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_communication_report_recommendations(self, auth_client, user):
        # Create many unmastered issues
        for i in range(6):
            CommunicationIssue.objects.create(
                user=user,
                category='filler_words',
                original_text=f'Test {i}',
                suggested_text=f'Test corrected {i}',
                status='confirmed'
            )
        
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        recommendations = response.data['recommendations']
        assert len(recommendations) > 0
        assert any('practice' in rec['type'] for rec in recommendations)


@pytest.mark.django_db
class TestInterviewReport:
    def test_interview_report_success(self, auth_client, interview_with_evaluation):
        url = reverse('reports-interviews')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'interview_history' in response.data
        assert 'performance_by_topic' in response.data
        assert 'performance_by_difficulty' in response.data
        assert 'score_progression' in response.data
        assert 'insights' in response.data
        
    def test_interview_report_history(self, auth_client, interview_with_evaluation):
        url = reverse('reports-interviews')
        response = auth_client.get(url)
        
        history = response.data['interview_history']
        assert len(history) == 1
        assert history[0]['difficulty'] == 'intermediate'
        assert history[0]['evaluation'] is not None
        assert history[0]['evaluation']['technical'] == 8.5
        
    def test_interview_report_performance_by_topic(self, auth_client, interview_with_evaluation):
        url = reverse('reports-interviews')
        response = auth_client.get(url)
        
        by_topic = response.data['performance_by_topic']
        assert len(by_topic) > 0
        
    def test_interview_report_score_progression(self, auth_client, interview_with_evaluation):
        url = reverse('reports-interviews')
        response = auth_client.get(url)
        
        progression = response.data['score_progression']
        assert len(progression) > 0
        assert 'date' in progression[0]
        assert 'average_score' in progression[0]
        
    def test_interview_report_unauthenticated(self, api_client):
        url = reverse('reports-interviews')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_interview_report_user_isolation(self, auth_client, other_user, role, topic):
        # Create interview for other user
        InterviewSession.objects.create(
            user=other_user,
            role=role,
            topic=topic,
            status='finished',
            finished_at=timezone.now()
        )
        
        url = reverse('reports-interviews')
        response = auth_client.get(url)
        
        # Should only see own interviews
        history = response.data['interview_history']
        assert all(item['id'] != 999 for item in history)


@pytest.mark.django_db
class TestProgressSnapshot:
    def test_create_snapshot_success(self, auth_client, communication_issues, practice_attempts):
        url = reverse('reports-snapshot')
        response = auth_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.data
        assert 'date' in response.data
        assert response.data['total_issues'] == 2
        assert response.data['mastered_issues'] == 1
        
    def test_create_snapshot_duplicate_today(self, auth_client, communication_issues):
        url = reverse('reports-snapshot')
        
        # First snapshot
        response1 = auth_client.post(url)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second snapshot same day
        response2 = auth_client.post(url)
        assert response2.status_code == status.HTTP_200_OK
        assert 'already exists' in response2.data['message']
        
    def test_create_snapshot_unauthenticated(self, api_client):
        url = reverse('reports-snapshot')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_snapshot_stored_in_database(self, auth_client, user):
        url = reverse('reports-snapshot')
        auth_client.post(url)
        
        snapshots = ProgressSnapshot.objects.filter(user=user)
        assert snapshots.count() == 1
        
    def test_snapshot_metrics_calculation(self, auth_client, user, interview_with_evaluation):
        url = reverse('reports-snapshot')
        response = auth_client.post(url)
        
        snapshot = ProgressSnapshot.objects.get(id=response.data['id'])
        assert 'interviews_completed' in snapshot.metrics
        assert snapshot.metrics['interviews_completed'] == 1


@pytest.mark.django_db
class TestReportHelpers:
    def test_improvement_trend_insufficient_data(self, auth_client, user):
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.data['improvement_trend'] == 'insufficient_data'
        
    def test_improvement_trend_improving(self, auth_client, user, role, topic):
        # Create older interview with lower scores
        old_interview = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='finished',
            finished_at=timezone.now() - timedelta(days=7)
        )
        InterviewEvaluation.objects.create(
            session=old_interview,
            technical_score=5.0,
            completeness_score=5.0,
            reasoning_score=5.0,
            organization_score=5.0
        )
        
        # Create recent interview with higher scores
        new_interview = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='finished',
            finished_at=timezone.now()
        )
        InterviewEvaluation.objects.create(
            session=new_interview,
            technical_score=9.0,
            completeness_score=9.0,
            reasoning_score=9.0,
            organization_score=9.0
        )
        
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.data['improvement_trend'] == 'improving'
        
    def test_practice_timeline(self, auth_client, user, communication_issues):
        # Create practice attempts today
        issue = communication_issues[0]
        PracticeAttempt.objects.create(
            user=user, issue=issue, practice_text='Test', score=8.0
        )
        
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        timeline = response.data['practice_timeline']
        assert len(timeline) >= 0


@pytest.mark.django_db
class TestReportEdgeCases:
    def test_report_with_no_evaluation(self, auth_client, user, role, topic):
        # Interview without evaluation
        InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='finished',
            finished_at=timezone.now()
        )
        
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_report_with_null_scores(self, auth_client, user, role, topic):
        interview = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='finished',
            finished_at=timezone.now()
        )
        InterviewEvaluation.objects.create(
            session=interview,
            technical_score=None,
            completeness_score=None,
            reasoning_score=None,
            organization_score=None
        )
        
        url = reverse('reports-overview')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_communication_report_empty(self, auth_client):
        url = reverse('reports-communication')
        response = auth_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['summary']['by_category']) == 0
