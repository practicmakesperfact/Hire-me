import pytest
from django.urls import reverse
from apps.interviews.models import Role, Topic, InterviewSession, InterviewTurn


@pytest.mark.django_db
class TestRoleAPI:
    
    def test_list_roles(self, authenticated_client):
        Role.objects.create(name='Software Engineer', description='Backend dev')
        url = reverse('role-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_create_role(self, authenticated_client):
        url = reverse('role-list')
        data = {'name': 'Data Scientist', 'description': 'ML engineer'}
        response = authenticated_client.post(url, data, content_type='application/json')
        
        assert response.status_code == 201
        assert Role.objects.filter(name='Data Scientist').exists()


@pytest.mark.django_db
class TestTopicAPI:
    
    def test_list_topics(self, authenticated_client):
        Topic.objects.create(name='Python', difficulty_level='intermediate')
        url = reverse('topic-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_filter_topics_by_difficulty(self, authenticated_client):
        Topic.objects.create(name='Python', difficulty_level='beginner')
        Topic.objects.create(name='Django', difficulty_level='advanced')
        
        url = reverse('topic-list') + '?difficulty_level=beginner'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1


@pytest.mark.django_db
class TestInterviewSessionAPI:
    
    def test_create_interview_session(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        
        url = reverse('interview-list')
        data = {
            'role': role.id,
            'topic': topic.id,
            'difficulty': 'intermediate',
            'interview_type': 'technical'
        }
        response = authenticated_client.post(url, data, content_type='application/json')
        
        assert response.status_code == 201
        assert response.json()['status'] == 'ready'
        assert response.json()['user'] == user.id
    
    def test_list_user_interviews_only(self, authenticated_client, user, django_user_model):
        other_user = django_user_model.objects.create_user(
            username='other', password='pass'
        )
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        
        InterviewSession.objects.create(user=user, role=role, topic=topic)
        InterviewSession.objects.create(user=other_user, role=role, topic=topic)
        
        url = reverse('interview-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_start_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='ready'
        )
        
        url = reverse('interview-start', kwargs={'pk': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.status == 'asking'
        assert session.started_at is not None
    
    def test_cannot_start_already_started_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='asking'
        )
        
        url = reverse('interview-start', kwargs={'pk': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 400
    
    def test_pause_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='asking'
        )
        
        url = reverse('interview-pause', kwargs={'pk': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.status == 'paused'
    
    def test_resume_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='paused'
        )
        
        url = reverse('interview-resume', kwargs={'pk': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.status == 'asking'
    
    def test_finish_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='asking'
        )
        
        url = reverse('interview-finish', kwargs={'pk': session.id})
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        session.refresh_from_db()
        assert session.status == 'finished'
        assert session.finished_at is not None


@pytest.mark.django_db
class TestInterviewTurnAPI:
    
    def test_add_turn_to_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='asking'
        )
        
        url = reverse('interview-turns', kwargs={'pk': session.id})
        data = {
            'question_text': 'What is a decorator?',
            'answer_text': 'A function that wraps another function'
        }
        response = authenticated_client.post(url, data, content_type='application/json')
        
        assert response.status_code == 201
        assert response.json()['turn_number'] == 1
        assert session.turns.count() == 1
    
    def test_turn_numbers_increment(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='asking'
        )
        
        url = reverse('interview-turns', kwargs={'pk': session.id})
        
        # First turn
        authenticated_client.post(url, {
            'question_text': 'Q1',
            'answer_text': 'A1'
        }, content_type='application/json')
        
        # Second turn
        response = authenticated_client.post(url, {
            'question_text': 'Q2',
            'answer_text': 'A2'
        }, content_type='application/json')
        
        assert response.json()['turn_number'] == 2
    
    def test_cannot_add_turn_to_finished_interview(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, status='finished'
        )
        
        url = reverse('interview-turns', kwargs={'pk': session.id})
        data = {'question_text': 'Q1', 'answer_text': 'A1'}
        response = authenticated_client.post(url, data, content_type='application/json')
        
        assert response.status_code == 400
    
    def test_retrieve_interview_with_turns(self, authenticated_client, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic
        )
        InterviewTurn.objects.create(
            session=session,
            turn_number=1,
            question_text='What is Python?',
            answer_text='A programming language'
        )
        
        url = reverse('interview-detail', kwargs={'pk': session.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'turns' in response.json()
        assert len(response.json()['turns']) == 1
