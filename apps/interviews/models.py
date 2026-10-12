from django.db import models
from django.conf import settings


class Role(models.Model):
    """Interview role/position."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Topic(models.Model):
    """Interview topic/category."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='intermediate'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class InterviewSession(models.Model):
    """Interview session."""
    STATUS_CHOICES = [
        ('ready', 'Ready'),
        ('asking', 'Asking'),
        ('listening', 'Listening'),
        ('transcribing', 'Transcribing'),
        ('processing', 'Processing'),
        ('finished', 'Finished'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready')
    difficulty = models.CharField(max_length=20, default='intermediate')
    interview_type = models.CharField(max_length=50, default='technical')
    job_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'interview_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.topic} ({self.status})"



class InterviewTurn(models.Model):
    """A single question-answer turn in an interview."""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='turns')
    turn_number = models.IntegerField()
    question_text = models.TextField()
    question_audio = models.FileField(upload_to='audio/questions/', null=True, blank=True)
    answer_text = models.TextField(blank=True)
    answer_audio = models.FileField(upload_to='audio/answers/', null=True, blank=True)
    transcription_confidence = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'interview_turns'
        ordering = ['session', 'turn_number']
        unique_together = ['session', 'turn_number']
        indexes = [
            models.Index(fields=['session', 'turn_number']),
        ]
    
    def __str__(self):
        return f"Turn {self.turn_number} - {self.session}"


class InterviewEvaluation(models.Model):
    """Evaluation of an interview session."""
    session = models.OneToOneField(InterviewSession, on_delete=models.CASCADE, related_name='evaluation')
    technical_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)
    reasoning_score = models.FloatField(null=True, blank=True)
    organization_score = models.FloatField(null=True, blank=True)
    overall_feedback = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'interview_evaluations'
    
    def __str__(self):
        return f"Evaluation - {self.session}"
