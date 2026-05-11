from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatMessageViewSet, HintRequestViewSet, StruggleDetectionViewSet, PeerMatchViewSet

router = DefaultRouter()
router.register(r'messages', ChatMessageViewSet, basename='message')
router.register(r'hints', HintRequestViewSet, basename='hint')
router.register(r'struggles', StruggleDetectionViewSet, basename='struggle')
router.register(r'peer-matches', PeerMatchViewSet, basename='peer-match')

urlpatterns = [
    path('chat/', include(router.urls)),
]
