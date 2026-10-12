from rest_framework import serializers
from .models import PracticeAttempt, ProgressSnapshot


class PracticeAttemptSerializer(serializers.ModelSerializer):
    issue_category = serializers.CharField(source='issue.category', read_only=True)
    issue_original_text = serializers.CharField(source='issue.original_text', read_only=True)
    
    class Meta:
        model = PracticeAttempt
        fields = [
            'id', 'user', 'issue', 'issue_category', 'issue_original_text',
            'attempt_audio', 'attempt_text', 'transcription', 'feedback',
            'score', 'metrics', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ProgressSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressSnapshot
        fields = [
            'id', 'user', 'snapshot_date', 'total_issues',
            'mastered_issues', 'practicing_issues', 'practice_sessions',
            'metrics', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
