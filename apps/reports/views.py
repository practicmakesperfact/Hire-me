from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Q
from datetime import timedelta
from apps.interviews.models import InterviewSession, InterviewEvaluation
from apps.communication.models import CommunicationIssue
from apps.practice.models import PracticeAttempt, ProgressSnapshot


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def overview_report_view(request):
    """Get comprehensive overview report."""
    user = request.user
    
    # Interview statistics
    total_interviews = InterviewSession.objects.filter(user=user).count()
    finished_interviews = InterviewSession.objects.filter(
        user=user, status='finished'
    ).count()
    
    # Recent activity (last 30 days)
    recent_date = timezone.now() - timedelta(days=30)
    recent_interviews = InterviewSession.objects.filter(
        user=user,
        created_at__gte=recent_date
    ).count()
    
    # Average scores from evaluations
    evaluations = InterviewEvaluation.objects.filter(
        session__user=user
    )
    
    avg_scores = {
        'technical': None,
        'completeness': None,
        'reasoning': None,
        'organization': None
    }
    
    if evaluations.exists():
        avg_scores = {
            'technical': evaluations.aggregate(Avg('technical_score'))['technical_score__avg'],
            'completeness': evaluations.aggregate(Avg('completeness_score'))['completeness_score__avg'],
            'reasoning': evaluations.aggregate(Avg('reasoning_score'))['reasoning_score__avg'],
            'organization': evaluations.aggregate(Avg('organization_score'))['organization_score__avg']
        }
        
        # Round scores
        avg_scores = {k: round(v, 2) if v else None for k, v in avg_scores.items()}
    
    # Communication issues
    total_issues = CommunicationIssue.objects.filter(user=user).count()
    mastered_issues = CommunicationIssue.objects.filter(
        user=user, status='mastered'
    ).count()
    
    # Practice statistics
    total_practice_attempts = PracticeAttempt.objects.filter(user=user).count()
    recent_practice = PracticeAttempt.objects.filter(
        user=user,
        created_at__gte=recent_date
    ).count()
    
    # Calculate improvement trend
    improvement_trend = _calculate_improvement_trend(user)
    
    return Response({
        'user': {
            'username': user.username,
            'email': user.email
        },
        'interviews': {
            'total': total_interviews,
            'finished': finished_interviews,
            'recent_30d': recent_interviews,
            'completion_rate': round((finished_interviews / total_interviews * 100), 1) if total_interviews > 0 else 0
        },
        'performance': {
            'average_scores': avg_scores,
            'evaluations_count': evaluations.count()
        },
        'communication': {
            'total_issues': total_issues,
            'mastered': mastered_issues,
            'mastery_rate': round((mastered_issues / total_issues * 100), 1) if total_issues > 0 else 0
        },
        'practice': {
            'total_attempts': total_practice_attempts,
            'recent_30d': recent_practice
        },
        'improvement_trend': improvement_trend
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def communication_report_view(request):
    """Get detailed communication improvement report."""
    user = request.user
    
    # Issues by category
    issues_by_category = CommunicationIssue.objects.filter(
        user=user
    ).values('category').annotate(
        total=Count('id'),
        mastered=Count('id', filter=Q(status='mastered')),
        practicing=Count('id', filter=Q(status='practicing'))
    ).order_by('-total')
    
    # Issues by status
    issues_by_status = CommunicationIssue.objects.filter(
        user=user
    ).values('status').annotate(count=Count('id'))
    
    # Most practiced issues
    most_practiced = CommunicationIssue.objects.filter(
        user=user
    ).order_by('-practice_count')[:10].values(
        'id', 'category', 'original_text', 'practice_count', 'status'
    )
    
    # Practice history over time
    practice_timeline = _get_practice_timeline(user, days=30)
    
    # Common issue patterns
    common_patterns = _analyze_common_patterns(user)
    
    return Response({
        'summary': {
            'by_category': list(issues_by_category),
            'by_status': list(issues_by_status)
        },
        'most_practiced': list(most_practiced),
        'practice_timeline': practice_timeline,
        'common_patterns': common_patterns,
        'recommendations': _generate_recommendations(user)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interview_report_view(request):
    """Get detailed interview performance report."""
    user = request.user
    
    # Interview history
    interviews = InterviewSession.objects.filter(
        user=user, status='finished'
    ).order_by('-finished_at')[:20]
    
    interview_history = []
    for interview in interviews:
        eval_data = None
        if hasattr(interview, 'evaluation'):
            eval_data = {
                'technical': interview.evaluation.technical_score,
                'completeness': interview.evaluation.completeness_score,
                'reasoning': interview.evaluation.reasoning_score,
                'organization': interview.evaluation.organization_score
            }
        
        interview_history.append({
            'id': interview.id,
            'topic': interview.topic.name if interview.topic else None,
            'difficulty': interview.difficulty,
            'date': interview.finished_at.isoformat() if interview.finished_at else None,
            'turn_count': interview.turns.count(),
            'evaluation': eval_data
        })
    
    # Performance by topic
    performance_by_topic = _get_performance_by_topic(user)
    
    # Performance by difficulty
    performance_by_difficulty = _get_performance_by_difficulty(user)
    
    # Score progression over time
    score_progression = _get_score_progression(user)
    
    return Response({
        'interview_history': interview_history,
        'performance_by_topic': performance_by_topic,
        'performance_by_difficulty': performance_by_difficulty,
        'score_progression': score_progression,
        'insights': _generate_interview_insights(user)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_snapshot_view(request):
    """Create a progress snapshot."""
    user = request.user
    snapshot_date = timezone.now().date()
    
    # Check if snapshot already exists for today
    if ProgressSnapshot.objects.filter(user=user, snapshot_date=snapshot_date).exists():
        return Response({
            'message': 'Snapshot already exists for today'
        })
    
    # Calculate metrics
    total_issues = CommunicationIssue.objects.filter(user=user).count()
    mastered_issues = CommunicationIssue.objects.filter(
        user=user, status='mastered'
    ).count()
    practicing_issues = CommunicationIssue.objects.filter(
        user=user, status='practicing'
    ).count()
    
    practice_sessions = PracticeAttempt.objects.filter(
        user=user,
        created_at__date=snapshot_date
    ).count()
    
    # Additional metrics
    metrics = {
        'interviews_completed': InterviewSession.objects.filter(
            user=user, status='finished'
        ).count(),
        'avg_practice_score': _get_avg_practice_score(user)
    }
    
    # Create snapshot
    snapshot = ProgressSnapshot.objects.create(
        user=user,
        snapshot_date=snapshot_date,
        total_issues=total_issues,
        mastered_issues=mastered_issues,
        practicing_issues=practicing_issues,
        practice_sessions=practice_sessions,
        metrics=metrics
    )
    
    return Response({
        'id': snapshot.id,
        'date': snapshot.snapshot_date.isoformat(),
        'total_issues': total_issues,
        'mastered_issues': mastered_issues,
        'message': 'Snapshot created successfully'
    })


# Helper functions

def _calculate_improvement_trend(user):
    """Calculate improvement trend based on recent scores."""
    recent_evals = InterviewEvaluation.objects.filter(
        session__user=user
    ).order_by('-created_at')[:5]
    
    if recent_evals.count() < 2:
        return 'insufficient_data'
    
    recent_avg = sum([
        (e.technical_score or 0) + (e.completeness_score or 0) +
        (e.reasoning_score or 0) + (e.organization_score or 0)
        for e in recent_evals[:2]
    ]) / 8  # 2 evals * 4 scores
    
    older_avg = sum([
        (e.technical_score or 0) + (e.completeness_score or 0) +
        (e.reasoning_score or 0) + (e.organization_score or 0)
        for e in recent_evals[2:4]
    ]) / 8
    
    if recent_avg > older_avg + 0.5:
        return 'improving'
    elif recent_avg < older_avg - 0.5:
        return 'declining'
    else:
        return 'stable'


def _get_practice_timeline(user, days=30):
    """Get practice activity timeline."""
    start_date = timezone.now() - timedelta(days=days)
    
    timeline = []
    for i in range(days):
        date = (start_date + timedelta(days=i)).date()
        count = PracticeAttempt.objects.filter(
            user=user,
            created_at__date=date
        ).count()
        
        if count > 0:
            timeline.append({
                'date': date.isoformat(),
                'attempts': count
            })
    
    return timeline


def _analyze_common_patterns(user):
    """Analyze common issue patterns."""
    # Most common categories
    top_categories = CommunicationIssue.objects.filter(
        user=user
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:3]
    
    return {
        'top_categories': list(top_categories)
    }


def _generate_recommendations(user):
    """Generate improvement recommendations."""
    recommendations = []
    
    # Check for unmastered issues
    unmastered = CommunicationIssue.objects.filter(
        user=user,
        status__in=['confirmed', 'practicing']
    ).count()
    
    if unmastered > 5:
        recommendations.append({
            'type': 'practice',
            'priority': 'high',
            'message': f'You have {unmastered} issues to practice. Focus on mastering them.'
        })
    
    # Check practice frequency
    recent_practice = PracticeAttempt.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    if recent_practice < 5:
        recommendations.append({
            'type': 'consistency',
            'priority': 'medium',
            'message': 'Try to practice more consistently. Aim for at least 1 practice session per day.'
        })
    
    return recommendations


def _get_performance_by_topic(user):
    """Get performance breakdown by topic."""
    topics = InterviewSession.objects.filter(
        user=user, status='finished'
    ).values('topic__name').annotate(
        count=Count('id'),
        avg_technical=Avg('evaluation__technical_score'),
        avg_completeness=Avg('evaluation__completeness_score')
    ).order_by('-count')
    
    return list(topics)


def _get_performance_by_difficulty(user):
    """Get performance breakdown by difficulty."""
    difficulties = InterviewSession.objects.filter(
        user=user, status='finished'
    ).values('difficulty').annotate(
        count=Count('id'),
        avg_score=Avg('evaluation__technical_score')
    )
    
    return list(difficulties)


def _get_score_progression(user):
    """Get score progression over time."""
    evals = InterviewEvaluation.objects.filter(
        session__user=user
    ).order_by('created_at')[:20]
    
    progression = []
    for eval in evals:
        avg_score = None
        if all([eval.technical_score, eval.completeness_score,
                eval.reasoning_score, eval.organization_score]):
            avg_score = (
                eval.technical_score + eval.completeness_score +
                eval.reasoning_score + eval.organization_score
            ) / 4
        
        progression.append({
            'date': eval.created_at.isoformat(),
            'average_score': round(avg_score, 2) if avg_score else None
        })
    
    return progression


def _generate_interview_insights(user):
    """Generate insights from interview data."""
    insights = []
    
    total_interviews = InterviewSession.objects.filter(
        user=user, status='finished'
    ).count()
    
    if total_interviews >= 5:
        insights.append({
            'type': 'milestone',
            'message': f'Great progress! You\'ve completed {total_interviews} interviews.'
        })
    
    return insights


def _get_avg_practice_score(user):
    """Get average practice score."""
    attempts = PracticeAttempt.objects.filter(
        user=user,
        score__isnull=False
    )
    
    if attempts.exists():
        return round(attempts.aggregate(Avg('score'))['score__avg'], 2)
    
    return None
