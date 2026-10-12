from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import CommunicationIssue
from .serializers import CommunicationIssueSerializer
from apps.interviews.models import InterviewSession
from services.communication_analyzer.issue_detector import IssueDetector


class CommunicationIssueViewSet(viewsets.ModelViewSet):
    """ViewSet for communication issues."""
    serializer_class = CommunicationIssueSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'category', 'session']
    
    def get_queryset(self):
        return CommunicationIssue.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm issue as valid."""
        issue = self.get_object()
        issue.status = 'confirmed'
        issue.save()
        
        serializer = self.get_serializer(issue)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss issue as false positive."""
        issue = self.get_object()
        issue.status = 'dismissed'
        issue.save()
        
        serializer = self.get_serializer(issue)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def start_practicing(self, request, pk=None):
        """Mark issue as being practiced."""
        issue = self.get_object()
        issue.status = 'practicing'
        issue.save()
        
        serializer = self.get_serializer(issue)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_session_view(request, session_id):
    """Analyze entire interview session for communication issues."""
    session = get_object_or_404(
        InterviewSession,
        id=session_id,
        user=request.user
    )
    
    detector = IssueDetector()
    result = detector.batch_analyze_session(session, save=True)
    
    return Response({
        'session_id': session_id,
        'stats': result['stats'],
        'message': f"Analyzed {result['stats']['analyzed_turns']} turns, found {result['stats']['total_issues']} issues"
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def issue_summary_view(request):
    """Get summary of user's communication issues."""
    issues = CommunicationIssue.objects.filter(user=request.user)
    
    summary = {
        'total_issues': issues.count(),
        'by_status': {},
        'by_category': {},
        'needs_review': issues.filter(status='needs_review').count(),
        'practicing': issues.filter(status='practicing').count(),
        'mastered': issues.filter(status='mastered').count(),
    }
    
    # Count by status
    for status_choice, _ in CommunicationIssue.STATUS_CHOICES:
        count = issues.filter(status=status_choice).count()
        if count > 0:
            summary['by_status'][status_choice] = count
    
    # Count by category
    for category_choice, _ in CommunicationIssue.CATEGORY_CHOICES:
        count = issues.filter(category=category_choice).count()
        if count > 0:
            summary['by_category'][category_choice] = count
    
    return Response(summary)
