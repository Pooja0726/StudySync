from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudyRoom, RoomMember, SessionSummary, KnowledgeGraph


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class RoomMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = RoomMember
        fields = ['id', 'user', 'struggle_level', 'joined_at', 'is_active', 'last_activity']
        read_only_fields = ['id', 'joined_at', 'last_activity']


class StudyRoomSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    members = RoomMemberSerializer(many=True, read_only=True)
    current_member_count = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = StudyRoom
        fields = [
            'id', 'topic', 'title', 'description', 'created_by',
            'max_members', 'current_member_count', 'is_full', 'is_active',
            'members', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'members', 'created_at', 'updated_at']
    
    def get_current_member_count(self, obj):
        return obj.current_member_count
    
    def get_is_full(self, obj):
        return obj.is_full


class SessionSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionSummary
        fields = [
            'id', 'room', 'session_start', 'session_end', 'key_learnings',
            'weak_topics', 'strong_topics', 'next_suggested_topics',
            'average_struggle_level', 'total_messages', 'total_hints_given',
            'peer_matches', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class KnowledgeGraphSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = KnowledgeGraph
        fields = [
            'id', 'username', 'topics_mastered', 'learning_velocity',
            'current_streak', 'max_streak', 'placement_readiness_score',
            'total_sessions', 'total_study_hours', 'average_struggle_level',
            'preferred_learning_time', 'last_study_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'username', 'topics_mastered', 'learning_velocity',
            'placement_readiness_score', 'created_at', 'updated_at'
        ]
