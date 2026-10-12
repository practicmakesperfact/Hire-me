from rest_framework import serializers
from .models import Role, Topic, InterviewSession, InterviewTurn, InterviewEvaluation


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'difficulty_level', 'created_at']
        read_only_fields = ['id', 'created_at']


class InterviewTurnSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewTurn
        fields = [
            'id', 'turn_number', 'question_text', 'question_audio',
            'answer_text', 'answer_audio', 'transcription_confidence',
            'created_at', 'answered_at'
        ]
        read_only_fields = ['id', 'created_at']


class InterviewEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewEvaluation
        fields = [
            'id', 'technical_score', 'completeness_score', 'reasoning_score',
            'organization_score', 'overall_feedback', 'strengths',
            'improvements', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class InterviewSessionSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    turn_count = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'user', 'role', 'role_name', 'topic', 'topic_name',
            'status', 'difficulty', 'interview_type', 'job_description',
            'created_at', 'started_at', 'finished_at', 'turn_count'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'started_at', 'finished_at']
    
    def get_turn_count(self, obj):
        return obj.turns.count()


class InterviewSessionDetailSerializer(InterviewSessionSerializer):
    turns = InterviewTurnSerializer(many=True, read_only=True)
    evaluation = InterviewEvaluationSerializer(read_only=True)
    
    class Meta(InterviewSessionSerializer.Meta):
        fields = InterviewSessionSerializer.Meta.fields + ['turns', 'evaluation']
