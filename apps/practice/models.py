from django.db import models
from django.conf import settings


class PracticeAttempt(models.Model):
    """User practice attempt for a communication issue."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    issue = models.ForeignKey('communication.CommunicationIssue', on_delete=models.CASCADE, related_name='attempts')
    attempt_audio = models.FileField(upload_to='audio/practice/', null=True, blank=True)
    attempt_text = models.TextField(blank=True)
    transcription = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    score = models.FloatField(null=True, blank=True)
    metrics = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'practice_attempts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['issue', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Attempt for {self.issue.id}"


class ProgressSnapshot(models.Model):
    """Aggregated progress metrics."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    snapshot_date = models.DateField()
    total_issues = models.IntegerField(default=0)
    mastered_issues = models.IntegerField(default=0)
    practicing_issues = models.IntegerField(default=0)
    practice_sessions = models.IntegerField(default=0)
    metrics = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'progress_snapshots'
        ordering = ['-snapshot_date']
        unique_together = ['user', 'snapshot_date']
        indexes = [
            models.Index(fields=['user', '-snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.snapshot_date}"
