from django.contrib import admin
from .models import ChatMessage, HintRequest, StruggleDetection, PeerMatch


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'message_type', 'is_moderated', 'created_at']
    list_filter = ['message_type', 'is_moderated', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['created_at']


@admin.register(HintRequest)
class HintRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'topic', 'current_stage', 'is_resolved', 'created_at']
    list_filter = ['topic', 'current_stage', 'is_resolved', 'created_at']
    search_fields = ['student__username', 'question']
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(StruggleDetection)
class StruggleDetectionAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'topic', 'struggle_source', 'severity_score', 'detected_at']
    list_filter = ['struggle_source', 'topic', 'detected_at']
    search_fields = ['student__username', 'topic']
    readonly_fields = ['detected_at']


@admin.register(PeerMatch)
class PeerMatchAdmin(admin.ModelAdmin):
    list_display = ['struggling_student', 'helping_peer', 'topic', 'was_helpful', 'duration_minutes', 'created_at']
    list_filter = ['topic', 'was_helpful', 'created_at']
    search_fields = ['struggling_student__username', 'helping_peer__username']
    readonly_fields = ['created_at']
