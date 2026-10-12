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
        """Finish an interview session."""
        session = self.get_object()
        
        if session.status in ['finished', 'cancelled']:
            return Response(
                {'error': f'Interview already {session.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'finished'
        session.finished_at = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
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
