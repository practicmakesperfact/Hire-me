from rest_framework import serializers
from .models import CommunicationIssue


class CommunicationIssueSerializer(serializers.ModelSerializer):
    session_id = serializers.IntegerField(source='session.id', read_only=True)
    turn_number = serializers.IntegerField(source='turn.turn_number', read_only=True, allow_null=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CommunicationIssue
        fields = [
            'id', 'user', 'session', 'session_id', 'turn', 'turn_number',
            'category', 'category_display', 'original_text', 'proposed_correction',
            'explanation', 'evidence', 'confidence_score', 'status', 'status_display',
            'practice_count', 'audio_segment', 'created_at', 'reviewed_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
