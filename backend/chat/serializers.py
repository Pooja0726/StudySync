from rest_framework import serializers
from .models import ChatMessage, HintRequest, StruggleDetection, PeerMatch
from rooms.serializers import UserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'room', 'sender', 'content', 'message_type',
            'is_moderated', 'moderation_reason', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'is_moderated', 'moderation_reason', 'created_at']


class HintRequestSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    
    class Meta:
        model = HintRequest
        fields = [
            'id', 'room', 'student', 'question', 'topic',
            'current_stage', 'stage_1_hint', 'stage_2_hint', 'stage_3_hint',
            'is_resolved', 'resolution_time', 'created_at', 'resolved_at'
        ]
        read_only_fields = [
            'id', 'student', 'stage_1_hint', 'stage_2_hint',
            'stage_3_hint', 'is_resolved', 'created_at', 'resolved_at'
        ]


class StruggleDetectionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    
    class Meta:
        model = StruggleDetection
        fields = [
            'id', 'room', 'student', 'topic', 'struggle_source',
            'struggle_signal', 'severity_score', 'is_matched', 'detected_at'
        ]
        read_only_fields = ['id', 'detected_at']


class PeerMatchSerializer(serializers.ModelSerializer):
    struggling_student = UserSerializer(read_only=True)
    helping_peer = UserSerializer(read_only=True)
    
    class Meta:
        model = PeerMatch
        fields = [
            'id', 'struggling_student', 'helping_peer', 'room', 'topic',
            'was_helpful', 'duration_minutes', 'notes', 'created_at', 'ended_at'
        ]
        read_only_fields = ['id', 'created_at']
