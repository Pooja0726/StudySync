from django.db import models
from django.contrib.auth.models import User
from rooms.models import StudyRoom


class ChatMessage(models.Model):
    """
    Stores chat messages in a study room with moderation and hint metadata.
    """
    MESSAGE_TYPE_CHOICES = [
        ('TEXT', 'Text Message'),
        ('HINT_REQUEST', 'Hint Request'),
        ('SYSTEM', 'System Message'),
    ]
    
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='TEXT')
    is_moderated = models.BooleanField(default=False)  # Flagged for off-topic
    moderation_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class HintRequest(models.Model):
    """
    Tracks 3-stage Socratic hint progression for each question.
    """
    HINT_STAGE_CHOICES = [
        (1, 'Conceptual Guidance'),
        (2, 'Directed Questions'),
        (3, 'Partial Solution'),
    ]
    
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='hint_requests')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hint_requests')
    question = models.TextField()
    topic = models.CharField(max_length=100)
    current_stage = models.IntegerField(choices=HINT_STAGE_CHOICES, default=1)
    
    stage_1_hint = models.TextField(blank=True)  # Conceptual
    stage_2_hint = models.TextField(blank=True)  # Guided
    stage_3_hint = models.TextField(blank=True)  # Partial solution
    
    is_resolved = models.BooleanField(default=False)
    resolution_time = models.FloatField(null=True, blank=True)  # Time to resolve in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Hint for {self.student.username}: {self.question[:50]}"


class StruggleDetection(models.Model):
    """
    Detects when students are struggling and tracks their struggle signals.
    """
    STRUGGLE_SOURCE_CHOICES = [
        ('MESSAGE', 'From chat message'),
        ('SOLVING_TIME', 'Excessive solving time'),
        ('HINT_REQUEST', 'Multiple hint requests'),
        ('MULTIPLE_ATTEMPTS', 'Multiple failed attempts'),
    ]
    
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='struggles')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='struggles')
    topic = models.CharField(max_length=100)
    struggle_source = models.CharField(max_length=20, choices=STRUGGLE_SOURCE_CHOICES)
    struggle_signal = models.TextField()  # What triggered the detection
    severity_score = models.FloatField(default=0.5)  # 0.0 to 1.0
    is_matched = models.BooleanField(default=False)  # Whether peer match was found
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.student.username} struggling with {self.topic}"


class PeerMatch(models.Model):
    """
    Records successful peer-to-peer help connections.
    Matches struggling students with peers who just solved the same topic.
    """
    struggling_student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_help'
    )
    helping_peer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='provided_help'
    )
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='peer_matches')
    topic = models.CharField(max_length=100)
    
    was_helpful = models.BooleanField(null=True, blank=True)  # Feedback from struggling student
    duration_minutes = models.FloatField(null=True, blank=True)  # Duration of help session
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.helping_peer.username} helping {self.struggling_student.username} with {self.topic}"
