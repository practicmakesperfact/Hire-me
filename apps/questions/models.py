from django.db import models


class Question(models.Model):
    """Pre-defined interview question."""
    topic = models.ForeignKey('interviews.Topic', on_delete=models.CASCADE)
    question_text = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='intermediate'
    )
    question_type = models.CharField(
        max_length=20,
        choices=[
            ('technical', 'Technical'),
            ('behavioral', 'Behavioral'),
            ('coding', 'Coding'),
        ],
        default='technical'
    )
    expected_answer = models.TextField(blank=True)
    key_points = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['topic', 'difficulty']),
        ]
    
    def __str__(self):
        return f"{self.topic.name} - {self.question_text[:50]}"
