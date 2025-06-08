from django.db import models
from .constants import EMOTIONS_CHOICES


class Conversation(models.Model):
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    agent_name = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20,default='pending')
    overall_compliance_score = models.IntegerField()
    primary_emotion = models.CharField(max_length=50, null=True, blank=True, default='neutral', choices=EMOTIONS_CHOICES)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField()
    sender = models.CharField(max_length=20, choices=[('customer', 'customer'), ('agent', 'agent')])
    emotion = models.CharField(max_length=50, null=True, blank=True, choices=EMOTIONS_CHOICES, default='neutral')
    emotion_confidence = models.FloatField()
    compliance_flags = models.JSONField(default=list, blank=True)

class AnalyticsData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    compliance_overview = models.JSONField()
    emotion_breakdown = models.JSONField()
    trends_data = models.JSONField()
