import pytest
from django.urls import reverse
from apps.interviews.models import Topic
from apps.questions.models import Question


@pytest.mark.django_db
class TestQuestionAPI:
    
    def test_list_questions(self, authenticated_client):
        topic = Topic.objects.create(name='Python')
        Question.objects.create(
            topic=topic,
            question_text='What is a list comprehension?',
            difficulty='intermediate'
        )
        
        url = reverse('question-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_create_question(self, authenticated_client):
        topic = Topic.objects.create(name='Django')
        
        url = reverse('question-list')
        data = {
            'topic': topic.id,
            'question_text': 'What is a Django model?',
            'difficulty': 'beginner',
            'question_type': 'technical',
            'expected_answer': 'A class that represents a database table'
        }
        response = authenticated_client.post(url, data, content_type='application/json')
        
        assert response.status_code == 201
        assert Question.objects.filter(question_text='What is a Django model?').exists()
    
    def test_filter_questions_by_topic(self, authenticated_client):
        python_topic = Topic.objects.create(name='Python')
        django_topic = Topic.objects.create(name='Django')
        
        Question.objects.create(topic=python_topic, question_text='Q1')
        Question.objects.create(topic=django_topic, question_text='Q2')
        
        url = reverse('question-list') + f'?topic={python_topic.id}'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_filter_questions_by_difficulty(self, authenticated_client):
        topic = Topic.objects.create(name='Python')
        Question.objects.create(topic=topic, question_text='Q1', difficulty='beginner')
        Question.objects.create(topic=topic, question_text='Q2', difficulty='advanced')
        
        url = reverse('question-list') + '?difficulty=beginner'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
    
    def test_filter_questions_by_type(self, authenticated_client):
        topic = Topic.objects.create(name='Python')
        Question.objects.create(
            topic=topic, question_text='Q1', question_type='technical'
        )
        Question.objects.create(
            topic=topic, question_text='Q2', question_type='behavioral'
        )
        
        url = reverse('question-list') + '?question_type=behavioral'
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert len(response.json()['results']) == 1
