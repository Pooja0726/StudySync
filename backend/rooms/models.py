from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class StudyRoom(models.Model):
    """
    Represents a topic-based study room where students collaborate.
    """
    TOPIC_CHOICES = [
        ('DSA', 'Data Structures & Algorithms'),
        ('APTITUDE', 'Aptitude'),
        ('MOCK', 'Mock Tests'),
        ('WEB', 'Web Development'),
        ('SYSTEM', 'System Design'),
    ]
    
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    max_members = models.IntegerField(default=6, validators=[MinValueValidator(2), MaxValueValidator(10)])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_topic_display()} - {self.title}"
    
    @property
    def current_member_count(self):
        return self.members.filter(is_active=True).count()
    
    @property
    def is_full(self):
        return self.current_member_count >= self.max_members


class RoomMember(models.Model):
    """
    Tracks membership and struggle state of students in a room.
    """
    STRUGGLE_LEVELS = [
        (0, 'No Struggle'),
        (1, 'Mild Struggle'),
        (2, 'Moderate Struggle'),
        (3, 'High Struggle'),
    ]
    
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    struggle_level = models.IntegerField(choices=STRUGGLE_LEVELS, default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('room', 'user')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.room.title}"


class SessionSummary(models.Model):
    """
    Stores intelligent summaries and insights from study sessions.
    """
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name='session_summaries')
    session_start = models.DateTimeField()
    session_end = models.DateTimeField()
    key_learnings = models.JSONField(default=list)
    weak_topics = models.JSONField(default=list)  # List of topics where students struggled
    strong_topics = models.JSONField(default=list)  # Topics well understood
    next_suggested_topics = models.JSONField(default=list)  # Recommended next topics
    average_struggle_level = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(3)])
    total_messages = models.IntegerField(default=0)
    total_hints_given = models.IntegerField(default=0)
    peer_matches = models.IntegerField(default=0)  # Successful peer-to-peer connections
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-session_end']
    
    def __str__(self):
        return f"Summary for {self.room.title} - {self.session_start}"


class KnowledgeGraph(models.Model):
    """
    Personal knowledge tracking for each student including mastery, velocity, and readiness.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='knowledge_graph')
    topics_mastered = models.JSONField(default=dict)  # {topic: mastery_level (0-1)}
    learning_velocity = models.FloatField(default=0.0)  # Topics mastered per week
    current_streak = models.IntegerField(default=0)  # Consecutive days studied
    max_streak = models.IntegerField(default=0)
    placement_readiness_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    total_sessions = models.IntegerField(default=0)
    total_study_hours = models.FloatField(default=0.0)
    average_struggle_level = models.FloatField(default=0.0)
    preferred_learning_time = models.CharField(max_length=10, default='morning')  # morning, afternoon, evening
    
    last_study_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Knowledge Graph"
    
    def calculate_readiness_score(self):
        """
        Calculate placement readiness score based on:
        - Topic mastery levels
        - Learning velocity
        - Current streak
        - Problem-solving speed
        """
        mastery_avg = sum(self.topics_mastered.values()) / len(self.topics_mastered) if self.topics_mastered else 0
        velocity_score = min(self.learning_velocity * 10, 20)  # Cap at 20 points
        streak_score = min(self.current_streak * 0.5, 15)  # Cap at 15 points
        
        readiness = (mastery_avg * 50) + velocity_score + streak_score
        self.placement_readiness_score = min(readiness, 100)
        self.save()
        return self.placement_readiness_score
