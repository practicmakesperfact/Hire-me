import pytest
from unittest.mock import Mock, patch
from services.llm.ollama_client import OllamaClient, get_ollama_client
from services.evaluation.interview_evaluator import InterviewEvaluator
from services.interview_orchestrator import InterviewOrchestrator
from apps.interviews.models import Role, Topic, InterviewSession, InterviewTurn


@pytest.mark.django_db
class TestOllamaClient:
    
    @patch('services.llm.ollama_client.requests.get')
    def test_is_available_success(self, mock_get):
        mock_get.return_value.status_code = 200
        
        client = OllamaClient()
        assert client.is_available() is True
    
    @patch('services.llm.ollama_client.requests.get')
    def test_is_available_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection failed")
        
        client = OllamaClient()
        assert client.is_available() is False
    
    @patch('services.llm.ollama_client.requests.post')
    def test_generate_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'response': 'This is a test response'
        }
        
        client = OllamaClient()
        response = client.generate("Test prompt")
        
        assert response == 'This is a test response'
    
    @patch('services.llm.ollama_client.requests.post')
    def test_generate_timeout(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        client = OllamaClient()
        response = client.generate("Test prompt")
        
        assert response is None
    
    @patch('services.llm.ollama_client.requests.post')
    def test_generate_structured(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'response': '{"score": 8.5, "feedback": "Good answer"}'
        }
        
        client = OllamaClient()
        response = client.generate_structured("Evaluate this answer")
        
        assert response is not None
        assert response['score'] == 8.5
    
    def test_get_ollama_client_singleton(self):
        client1 = get_ollama_client()
        client2 = get_ollama_client()
        
        assert client1 is client2


@pytest.mark.django_db
class TestInterviewOrchestrator:
    
    def test_select_question_from_bank(self, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python', difficulty_level='intermediate')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic, difficulty='intermediate'
        )
        
        from apps.questions.models import Question
        Question.objects.create(
            topic=topic,
            question_text='What is Python?',
            difficulty='intermediate',
            question_type='technical'
        )
        
        orchestrator = InterviewOrchestrator()
        question = orchestrator._select_question_from_bank(session)
        
        assert question is not None
        assert 'What is Python?' in question
    
    def test_build_conversation_context(self, user):
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic
        )
        
        InterviewTurn.objects.create(
            session=session,
            turn_number=1,
            question_text='Q1',
            answer_text='A1'
        )
        InterviewTurn.objects.create(
            session=session,
            turn_number=2,
            question_text='Q2',
            answer_text='A2'
        )
        
        orchestrator = InterviewOrchestrator()
        turns = session.turns.all()
        context = orchestrator._build_conversation_context(turns)
        
        assert 'Q1' in context
        assert 'A1' in context
        assert 'Q2' in context


@pytest.mark.django_db
class TestInterviewEvaluator:
    
    @patch('services.llm.ollama_client.OllamaClient.is_available')
    def test_evaluator_skips_when_unavailable(self, mock_available, user):
        mock_available.return_value = False
        
        role = Role.objects.create(name='Developer')
        topic = Topic.objects.create(name='Python')
        session = InterviewSession.objects.create(
            user=user, role=role, topic=topic
        )
        
        evaluator = InterviewEvaluator()
        result = evaluator.evaluate_interview(session)
        
        assert result is None
    
    def test_build_turns_context(self, user):
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
        
        evaluator = InterviewEvaluator()
        context = evaluator._build_turns_context(session)
        
        assert 'What is Python?' in context
        assert 'A programming language' in context
