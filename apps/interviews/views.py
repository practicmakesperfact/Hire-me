from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Role, Topic, InterviewSession, InterviewTurn
from .serializers import (
    RoleSerializer, TopicSerializer, InterviewSessionSerializer,
    InterviewSessionDetailSerializer, InterviewTurnSerializer
)
from services.interview_orchestrator import InterviewOrchestrator
from services.evaluation.interview_evaluator import InterviewEvaluator


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for interview roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


class TopicViewSet(viewsets.ModelViewSet):
    """ViewSet for interview topics."""
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['difficulty_level']


class InterviewSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for interview sessions."""
    serializer_class = InterviewSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orchestrator = InterviewOrchestrator()
        self.evaluator = InterviewEvaluator()
    
    def get_queryset(self):
        return InterviewSession.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InterviewSessionDetailSerializer
        return InterviewSessionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start an interview session."""
        session = self.get_object()
        
        if session.status != 'ready':
            return Response(
                {'error': 'Interview can only be started from ready state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'asking'
        session.started_at = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pause an interview session."""
        session = self.get_object()
        
        if session.status in ['finished', 'cancelled', 'paused']:
            return Response(
                {'error': f'Cannot pause interview in {session.status} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'paused'
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Resume a paused interview session."""
        session = self.get_object()
        
        if session.status != 'paused':
            return Response(
                {'error': 'Only paused interviews can be resumed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'asking'
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Finish an interview session and optionally generate evaluation."""
        session = self.get_object()
        
        if session.status in ['finished', 'cancelled']:
            return Response(
                {'error': f'Interview already {session.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        generate_eval = request.data.get('generate_evaluation', True)
        
        session.status = 'finished'
        session.finished_at = timezone.now()
        session.save()
        
        evaluation_data = None
        if generate_eval:
            evaluation_data = self.orchestrator.finish_interview_and_evaluate(session)
        
        serializer = self.get_serializer(session)
        response_data = serializer.data
        
        if evaluation_data:
            response_data['evaluation'] = evaluation_data
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'])
    def turns(self, request, pk=None):
        """Add a new turn to the interview."""
        session = self.get_object()
        
        if session.status not in ['asking', 'listening', 'processing']:
            return Response(
                {'error': f'Cannot add turn in {session.status} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        turn_number = session.turns.count() + 1
        
        serializer = InterviewTurnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                session=session,
                turn_number=turn_number
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def next_question(self, request, pk=None):
        """Generate next interview question using LLM."""
        session = self.get_object()
        
        if session.status not in ['asking', 'processing']:
            return Response(
                {'error': f'Cannot generate question in {session.status} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        use_llm = request.data.get('use_llm', True)
        question = self.orchestrator.generate_next_question(session, use_llm)
        
        if not question:
            return Response(
                {'error': 'Failed to generate question'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'question': question,
            'turn_number': session.turns.count() + 1
        })
    
    @action(detail=True, methods=['post'])
    def answer_and_continue(self, request, pk=None):
        """Submit answer and get next question in one call."""
        session = self.get_object()
        
        if session.status not in ['asking', 'listening', 'processing']:
            return Response(
                {'error': f'Cannot answer in {session.status} state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        answer_text = request.data.get('answer_text')
        current_question = request.data.get('question_text')
        
        if not answer_text or not current_question:
            return Response(
                {'error': 'answer_text and question_text are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = self.orchestrator.process_answer_and_generate_next(
            session, answer_text, current_question
        )
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Get interview evaluation report."""
        session = self.get_object()
        
        if session.status != 'finished':
            return Response(
                {'error': 'Interview must be finished to generate report'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if evaluation exists
        if hasattr(session, 'evaluation'):
            from .serializers import InterviewEvaluationSerializer
            serializer = InterviewEvaluationSerializer(session.evaluation)
            return Response(serializer.data)
        
        # Generate evaluation if not exists
        evaluation = self.evaluator.evaluate_interview(session)
        
        if evaluation:
            from .serializers import InterviewEvaluationSerializer
            serializer = InterviewEvaluationSerializer(evaluation)
            return Response(serializer.data)
        
        return Response(
            {'error': 'Failed to generate evaluation'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
