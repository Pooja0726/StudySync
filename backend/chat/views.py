from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import ChatMessage, HintRequest, StruggleDetection, PeerMatch
from .serializers import (
    ChatMessageSerializer, HintRequestSerializer, StruggleDetectionSerializer,
    PeerMatchSerializer
)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room', 'sender', 'message_type', 'is_moderated']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class HintRequestViewSet(viewsets.ModelViewSet):
    queryset = HintRequest.objects.all()
    serializer_class = HintRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room', 'student', 'topic', 'current_stage', 'is_resolved']
    ordering_fields = ['created_at', 'current_stage']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def next_stage(self, request, pk=None):
        """
        Progress to the next hint stage (Socratic method).
        """
        hint_request = self.get_object()
        
        if hint_request.current_stage >= 3:
            return Response(
                {'error': 'Already at final stage'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        hint_request.current_stage += 1
        # Generate next stage hint from AI service
        # This would call the hint engine
        hint_request.save()
        
        serializer = self.get_serializer(hint_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def resolve(self, request, pk=None):
        """
        Mark a hint request as resolved.
        """
        hint_request = self.get_object()
        hint_request.is_resolved = True
        hint_request.resolved_at = timezone.now()
        hint_request.save()
        
        serializer = self.get_serializer(hint_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StruggleDetectionViewSet(viewsets.ModelViewSet):
    queryset = StruggleDetection.objects.all()
    serializer_class = StruggleDetectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room', 'student', 'topic', 'struggle_source', 'is_matched']
    ordering_fields = ['detected_at', 'severity_score']
    ordering = ['-detected_at']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_struggles(self, request):
        """
        Get current user's recent struggle detections.
        """
        struggles = StruggleDetection.objects.filter(student=request.user).order_by('-detected_at')[:10]
        serializer = self.get_serializer(struggles, many=True)
        return Response(serializer.data)


class PeerMatchViewSet(viewsets.ModelViewSet):
    queryset = PeerMatch.objects.all()
    serializer_class = PeerMatchSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room', 'struggling_student', 'helping_peer', 'topic', 'was_helpful']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def end_session(self, request, pk=None):
        """
        End a peer match session and record feedback.
        """
        peer_match = self.get_object()
        was_helpful = request.data.get('was_helpful')
        notes = request.data.get('notes', '')
        
        from django.utils import timezone
        from datetime import datetime
        
        peer_match.ended_at = timezone.now()
        peer_match.was_helpful = was_helpful
        peer_match.notes = notes
        
        if peer_match.created_at:
            duration = (peer_match.ended_at - peer_match.created_at).total_seconds() / 60
            peer_match.duration_minutes = duration
        
        peer_match.save()
        serializer = self.get_serializer(peer_match)
        return Response(serializer.data, status=status.HTTP_200_OK)
