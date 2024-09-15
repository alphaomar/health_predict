# communication/models.py
from django.db import models
from django.conf import settings
import uuid

from django.utils import timezone


class Communication(models.Model):
    COMMUNICATION_TYPE_CHOICES = [
        ('text', 'Text Chat'),
        ('voice', 'Voice Call'),
        ('video', 'Video Call'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='initiated_communications')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_communications')
    communication_type = models.CharField(max_length=10, choices=COMMUNICATION_TYPE_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    room_id = models.CharField(max_length=255, blank=True, null=True)  # Room ID for video/voice chat

    def __str__(self):
        return f"{self.initiator.email} to {self.recipient.email} ({self.communication_type})"

    def mark_completed(self):
        """Mark communication as completed."""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.save()
