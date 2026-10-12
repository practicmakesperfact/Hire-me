from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for interview questions."""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['topic', 'difficulty', 'question_type']
