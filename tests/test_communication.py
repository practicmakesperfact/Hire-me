import pytest
from django.urls import reverse
from apps.interviews.models import Role, Topic, InterviewSession, InterviewTurn
from apps.communication.models import CommunicationIssue
from services.communication_analyzer.issue_detector import IssueDetector


@pytest.mark.django_db
class TestIssueDetector:
    
    def test_detect_filler_words(self):
        detector = IssueDetector()
        
        text = "Um, I think, like, Python is, uh, really, um, great. You know?"
        issues = detector._detect_filler_words(text)
        
        assert len(issues) > 0
        assert 'filler' in issues[0]['explanation'].lower()
    
    def test_detect_repetition_consecutive(self):
        detector = IssueDetector()
        
        text = "Python is is a great language"
        issues = detector._detect_repetition(text)
        
        assert len(issues) > 0
        assert 'repeated' in issues[0]['explanation'].lower()
    
    def test_detect_repetition_frequent(self):
        detector = IssueDetector()
        
        text = "Python Python Python Python is great and Python is popular"
        issues = detector._detect_repetition(text)
        
        assert len(issues) > 0
    
    def test_no_issues_for_clean_text(self):
        detector = IssueDetector()
        
        text = "Python is a high-level programming language with excellent readability."
        filler_issues = detector._detect_filler_words(text)
        repetition_issues = detector._detect_repetition(text)
        
        assert len(filler_issues) == 0
        assert len(repetition_issues) == 0
    
    def test_speaking_rate_analysis(self):
        detector = IssueDetector()
        
        text = "This is a test sentence with ten words total"
        duration = 3.0  # 3 seconds
        
        analysis = detector.analyze_speaking_rate(text, duration)
        
        assert 'words_per_minute' in analysis
        assert analysis['words_per_minute'] == 200  # 10 words in 3 sec = 200 wpm
    
    def test_analyze_turn_silent(self, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        turn = InterviewTurn.objects.create(
            session=session,
            turn_number=1,
            question_text='What is Python?',
            answer_text='Um, Python is, like, Python is, uh, a programming language'
        )
        
        detector = IssueDetector()
        issues = detector.analyze_turn_silent(turn, detect_grammar=False)
        
        assert len(issues) > 0
        assert all(isinstance(issue, CommunicationIssue) for issue in issues)
        assert all(issue.user == user for issue in issues)


@pytest.mark.django_db
class TestCommunicationAPI:
    
    def test_list_issues(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        CommunicationIssue.objects.create(
            user=user,
            session=session,
            category='grammar',
            original_text='I goes to store',
            proposed_correction='I go to the store',
            status='needs_review'
        )
        
        url = reverse('communication-issue-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_filter_issues_by_status(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 1', status='needs_review'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 2', status='confirmed'
        )
        
        url = reverse('communication-issue-list') + '?status=confirmed'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_confirm_issue(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test', status='needs_review'
        )
        
        url = reverse('communication-issue-confirm', kwargs={'pk': issue.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        issue.refresh_from_db()
        assert issue.status == 'confirmed'
    
    def test_dismiss_issue(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        issue = CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test', status='needs_review'
        )
        
        url = reverse('communication-issue-dismiss', kwargs={'pk': issue.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        issue.refresh_from_db()
        assert issue.status == 'dismissed'
    
    def test_issue_summary(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        CommunicationIssue.objects.create(
            user=user, session=session, category='grammar',
            original_text='Test 1', status='needs_review'
        )
        CommunicationIssue.objects.create(
            user=user, session=session, category='filler_words',
            original_text='Test 2', status='confirmed'
        )
        
        url = reverse('communication-summary')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        assert data['total_issues'] == 2
        assert 'by_category' in data
        assert 'by_status' in data
    
    def test_analyze_session(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(user=user, role=role, topic=topic)
        
        InterviewTurn.objects.create(
            session=session,
            turn_number=1,
            question_text='What is Python?',
            answer_text='Um, like, Python is, uh, a language'
        )
        
        url = reverse('communication-analyze-session', kwargs={'session_id': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        data = response.json()
        assert 'stats' in data
        assert data['stats']['analyzed_turns'] == 1
