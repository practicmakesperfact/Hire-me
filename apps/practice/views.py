from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from .models import PracticeAttempt, ProgressSnapshot
from .serializers import PracticeAttemptSerializer, ProgressSnapshotSerializer
from apps.communication.models import CommunicationIssue
from apps.communication.serializers import CommunicationIssueSerializer
from services.speech_to_text.whisper_service import get_whisper_service
from services.text_to_speech.piper_service import get_piper_service
from django.core.files.storage import default_storage
import os


class PracticeAttemptViewSet(viewsets.ModelViewSet):
    """ViewSet for practice attempts."""
    serializer_class = PracticeAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PracticeAttempt.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def practice_queue_view(request):
    """Get recommended issues to practice."""
    # Get confirmed issues that need practice
    issues = CommunicationIssue.objects.filter(
        user=request.user,
        status__in=['confirmed', 'practicing']
    ).order_by('-created_at')
    
    # Prioritize by practice count (fewer attempts first)
    issues = issues.order_by('practice_count', '-created_at')
    
    # Apply filters
    category = request.query_params.get('category')
    if category:
        issues = issues.filter(category=category)
    
    limit = int(request.query_params.get('limit', 10))
    issues = issues[:limit]
    
    serializer = CommunicationIssueSerializer(issues, many=True)
    return Response({
        'count': len(serializer.data),
        'items': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def practice_submit_view(request):
    """Submit a practice attempt."""
    issue_id = request.data.get('issue_id')
    attempt_text = request.data.get('attempt_text')
    
    if not issue_id:
        return Response(
            {'error': 'issue_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get issue
    issue = get_object_or_404(
        CommunicationIssue,
        id=issue_id,
        user=request.user
    )
    
    # Handle audio upload
    audio_file = request.FILES.get('audio')
    transcription = None
    
    if audio_file:
        # Save and transcribe audio
        temp_path = default_storage.save(f'temp/{audio_file.name}', audio_file)
        full_path = os.path.join(default_storage.location, temp_path)
        
        try:
            whisper = get_whisper_service()
            result = whisper.transcribe_file(full_path)
            
            if result:
                transcription = result['text']
                attempt_text = transcription  # Use transcription as attempt text
        finally:
            # Clean up temp file
            if default_storage.exists(temp_path):
                default_storage.delete(temp_path)
    
    if not attempt_text:
        return Response(
            {'error': 'Either attempt_text or audio is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Evaluate attempt
    feedback, score = _evaluate_practice_attempt(issue, attempt_text)
    
    # Create practice attempt
    attempt = PracticeAttempt.objects.create(
        user=request.user,
        issue=issue,
        attempt_text=attempt_text,
        transcription=transcription,
        feedback=feedback,
        score=score,
        metrics={'original': issue.original_text, 'target': issue.proposed_correction}
    )
    
    # Update issue
    issue.practice_count += 1
    if issue.status == 'confirmed':
        issue.status = 'practicing'
    issue.save()
    
    # Check if mastered (3+ attempts with good scores)
    recent_attempts = PracticeAttempt.objects.filter(
        issue=issue,
        score__gte=8.0
    ).count()
    
    if recent_attempts >= 3:
        issue.status = 'mastered'
        issue.save()
    
    serializer = PracticeAttemptSerializer(attempt)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_mastered_view(request, issue_id):
    """Manually mark issue as mastered."""
    issue = get_object_or_404(
        CommunicationIssue,
        id=issue_id,
        user=request.user
    )
    
    issue.status = 'mastered'
    issue.save()
    
    serializer = CommunicationIssueSerializer(issue)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def practice_history_view(request):
    """Get practice history."""
    issue_id = request.query_params.get('issue_id')
    
    attempts = PracticeAttempt.objects.filter(user=request.user)
    
    if issue_id:
        attempts = attempts.filter(issue_id=issue_id)
    
    attempts = attempts.order_by('-created_at')
    
    serializer = PracticeAttemptSerializer(attempts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_view(request):
    """Get user's overall practice progress."""
    user = request.user
    
    # Get issue counts by status
    total_issues = CommunicationIssue.objects.filter(user=user).count()
    needs_review = CommunicationIssue.objects.filter(user=user, status='needs_review').count()
    confirmed = CommunicationIssue.objects.filter(user=user, status='confirmed').count()
    practicing = CommunicationIssue.objects.filter(user=user, status='practicing').count()
    mastered = CommunicationIssue.objects.filter(user=user, status='mastered').count()
    dismissed = CommunicationIssue.objects.filter(user=user, status='dismissed').count()
    
    # Get practice stats
    total_attempts = PracticeAttempt.objects.filter(user=user).count()
    recent_attempts = PracticeAttempt.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Get average scores
    attempts_with_scores = PracticeAttempt.objects.filter(
        user=user,
        score__isnull=False
    )
    avg_score = None
    if attempts_with_scores.exists():
        avg_score = sum([a.score for a in attempts_with_scores]) / attempts_with_scores.count()
    
    # Get issues by category
    issues_by_category = CommunicationIssue.objects.filter(
        user=user,
        status__in=['confirmed', 'practicing', 'mastered']
    ).values('category').annotate(count=Count('id'))
    
    # Most practiced categories
    most_practiced = PracticeAttempt.objects.filter(
        user=user
    ).values('issue__category').annotate(
        attempt_count=Count('id')
    ).order_by('-attempt_count')[:5]
    
    return Response({
        'issues': {
            'total': total_issues,
            'needs_review': needs_review,
            'confirmed': confirmed,
            'practicing': practicing,
            'mastered': mastered,
            'dismissed': dismissed,
        },
        'practice': {
            'total_attempts': total_attempts,
            'recent_attempts_7d': recent_attempts,
            'average_score': round(avg_score, 2) if avg_score else None,
        },
        'categories': {
            'by_issue_count': list(issues_by_category),
            'most_practiced': list(most_practiced),
        },
        'completion_rate': round((mastered / total_issues * 100), 1) if total_issues > 0 else 0
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_reference_audio_view(request, issue_id):
    """Generate reference audio for practice."""
    issue = get_object_or_404(
        CommunicationIssue,
        id=issue_id,
        user=request.user
    )
    
    # Get target text (correction or original if no correction)
    target_text = issue.proposed_correction or issue.original_text
    
    if not target_text or len(target_text.strip()) == 0:
        return Response(
            {'error': 'No text available for audio generation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    piper = get_piper_service()
    
    if not piper.is_available():
        return Response(
            {'error': 'TTS service not available'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    audio_path = piper.synthesize(target_text)
    
    if audio_path:
        relative_path = os.path.relpath(audio_path, default_storage.location)
        return Response({
            'audio_url': default_storage.url(relative_path),
            'text': target_text
        })
    else:
        return Response(
            {'error': 'Audio generation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _evaluate_practice_attempt(issue: CommunicationIssue, attempt_text: str) -> tuple:
    """
    Evaluate practice attempt.
    Returns (feedback, score)
    """
    target = issue.proposed_correction or issue.original_text
    
    # Simple text comparison
    attempt_lower = attempt_text.lower().strip()
    target_lower = target.lower().strip()
    
    # Exact match
    if attempt_lower == target_lower:
        return "Perfect! Your attempt matches the target exactly.", 10.0
    
    # Check word overlap
    attempt_words = set(attempt_lower.split())
    target_words = set(target_lower.split())
    
    if len(target_words) == 0:
        return "Target text is empty.", 0.0
    
    overlap = len(attempt_words & target_words)
    total = len(target_words)
    score = (overlap / total) * 10
    
    if score >= 9:
        feedback = "Excellent! Very close to the target."
    elif score >= 7:
        feedback = "Good attempt! Most words are correct."
    elif score >= 5:
        feedback = "Decent attempt. Keep practicing."
    else:
        feedback = "Needs more practice. Try again."
    
    return feedback, round(score, 1)
