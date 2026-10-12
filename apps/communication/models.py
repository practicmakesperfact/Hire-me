from django.db import models
from django.conf import settings


class CommunicationIssue(models.Model):
    """Learning issue detected during interview."""
    CATEGORY_CHOICES = [
        ('pronunciation', 'Pronunciation Issue'),
        ('transcription_error', 'Transcription Error'),
        ('grammar', 'Grammar Issue'),
        ('vocabulary', 'Vocabulary Improvement'),
        ('filler_words', 'Filler Words'),
        ('repeated_words', 'Repeated Words'),
        ('speaking_rate', 'Speaking Rate'),
        ('pause_fluency', 'Pause/Fluency'),
        ('clarity', 'Sentence Clarity'),
        ('organization', 'Answer Organization'),
    ]
    
    STATUS_CHOICES = [
        ('needs_review', 'Needs Review'),
        ('confirmed', 'Confirmed'),
        ('dismissed', 'Dismissed'),
        ('practicing', 'Practicing'),
        ('mastered', 'Mastered'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey('interviews.InterviewSession', on_delete=models.CASCADE)
    turn = models.ForeignKey('interviews.InterviewTurn', on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    original_text = models.TextField()
    proposed_correction = models.TextField(blank=True)
    explanation = models.TextField(blank=True)
    evidence = models.JSONField(default=dict, blank=True)
    confidence_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='needs_review')
    practice_count = models.IntegerField(default=0)
    audio_segment = models.FileField(upload_to='audio/issues/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'communication_issues'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', 'category']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.status}"
