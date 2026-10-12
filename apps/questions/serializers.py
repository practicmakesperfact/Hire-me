from rest_framework import serializers
from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'topic', 'topic_name', 'question_text', 'difficulty',
            'question_type', 'expected_answer', 'key_points', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
