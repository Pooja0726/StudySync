from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudyRoomViewSet, RoomMemberViewSet, SessionSummaryViewSet,
    KnowledgeGraphViewSet
)

router = DefaultRouter()
router.register(r'rooms', StudyRoomViewSet, basename='room')
router.register(r'members', RoomMemberViewSet, basename='member')
router.register(r'session-summaries', SessionSummaryViewSet, basename='session-summary')
router.register(r'knowledge-graph', KnowledgeGraphViewSet, basename='knowledge-graph')

urlpatterns = [
    path('', include(router.urls)),
]
