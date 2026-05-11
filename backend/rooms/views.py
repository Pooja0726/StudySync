from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import StudyRoom, RoomMember, SessionSummary, KnowledgeGraph
from .serializers import (
    StudyRoomSerializer, RoomMemberSerializer, SessionSummarySerializer,
    KnowledgeGraphSerializer, UserSerializer
)


class StudyRoomViewSet(viewsets.ModelViewSet):
    queryset = StudyRoom.objects.all().prefetch_related('members')
    serializer_class = StudyRoomSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['topic', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', '-current_member_count']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def join(self, request, pk=None):
        """
        Join a study room.
        """
        room = self.get_object()
        
        if room.is_full:
            return Response(
                {'error': 'Room is full'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        member, created = RoomMember.objects.get_or_create(
            room=room,
            user=request.user,
            defaults={'is_active': True}
        )
        
        if not created and not member.is_active:
            member.is_active = True
            member.save()
        
        serializer = RoomMemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def leave(self, request, pk=None):
        """
        Leave a study room.
        """
        room = self.get_object()
        
        try:
            member = RoomMember.objects.get(room=room, user=request.user)
            member.is_active = False
            member.save()
            return Response(
                {'message': 'Successfully left the room'},
                status=status.HTTP_200_OK
            )
        except RoomMember.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this room'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def members(self, request, pk=None):
        """
        Get all active members of a room.
        """
        room = self.get_object()
        members = room.members.filter(is_active=True)
        serializer = RoomMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def session_summary(self, request, pk=None):
        """
        Get the latest session summary for a room.
        """
        room = self.get_object()
        summary = room.session_summaries.latest('created_at')
        serializer = SessionSummarySerializer(summary)
        return Response(serializer.data)


class RoomMemberViewSet(viewsets.ModelViewSet):
    queryset = RoomMember.objects.all()
    serializer_class = RoomMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room', 'user', 'is_active']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_rooms(self, request):
        """
        Get all rooms the current user is a member of.
        """
        members = RoomMember.objects.filter(user=request.user, is_active=True)
        rooms = [member.room for member in members]
        serializer = StudyRoomSerializer(rooms, many=True)
        return Response(serializer.data)


class SessionSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SessionSummary.objects.all()
    serializer_class = SessionSummarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['room']
    ordering_fields = ['session_start', 'session_end']
    ordering = ['-session_end']


class KnowledgeGraphViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = KnowledgeGraphSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return KnowledgeGraph.objects.all()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get the current user's knowledge graph.
        """
        try:
            knowledge_graph = KnowledgeGraph.objects.get(user=request.user)
            serializer = self.get_serializer(knowledge_graph)
            return Response(serializer.data)
        except KnowledgeGraph.DoesNotExist:
            return Response(
                {'error': 'Knowledge graph not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def leaderboard(self, request):
        """
        Get leaderboard based on placement readiness score.
        """
        limit = int(request.query_params.get('limit', 10))
        leaderboard = KnowledgeGraph.objects.order_by('-placement_readiness_score')[:limit]
        serializer = self.get_serializer(leaderboard, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def calculate_readiness(self, request):
        """
        Recalculate placement readiness score.
        """
        try:
            knowledge_graph = KnowledgeGraph.objects.get(user=request.user)
            score = knowledge_graph.calculate_readiness_score()
            return Response(
                {'placement_readiness_score': score},
                status=status.HTTP_200_OK
            )
        except KnowledgeGraph.DoesNotExist:
            return Response(
                {'error': 'Knowledge graph not found'},
                status=status.HTTP_404_NOT_FOUND
            )
