from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model with additional profile fields."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
