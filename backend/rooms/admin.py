from django.contrib import admin
from .models import StudyRoom, RoomMember, SessionSummary, KnowledgeGraph


@admin.register(StudyRoom)
class StudyRoomAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'created_by', 'current_member_count', 'is_active', 'created_at']
    list_filter = ['topic', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'struggle_level', 'is_active', 'joined_at']
    list_filter = ['is_active', 'struggle_level', 'joined_at']
    search_fields = ['user__username', 'room__title']


@admin.register(SessionSummary)
class SessionSummaryAdmin(admin.ModelAdmin):
    list_display = ['room', 'session_start', 'session_end', 'average_struggle_level', 'total_messages']
    list_filter = ['created_at', 'average_struggle_level']
    search_fields = ['room__title']
    readonly_fields = ['created_at']


@admin.register(KnowledgeGraph)
class KnowledgeGraphAdmin(admin.ModelAdmin):
    list_display = ['user', 'placement_readiness_score', 'current_streak', 'total_sessions', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
