# common/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

class SentSMS(models.Model):
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=100, blank=True, null=True)  # Optional: store API status
    
    class Meta:
        app_label = "common"  

    def __str__(self):
        return f"SMS to {self.phone_number} at {self.sent_at.strftime('%Y-%m-%d %H:%M')}"


