import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rooms.models import StudyRoom, RoomMember
from .models import ChatMessage, HintRequest, StruggleDetection


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat in study rooms.
    Handles message sending, hint requests, and struggle detection.
    """
    
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Mark user as active in room
        await self.mark_user_active()
        
        # Notify others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def disconnect(self, close_code):
        # Mark user as inactive
        await self.mark_user_inactive()
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'username': self.user.username,
                'user_id': self.user.id
            }
        )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_chat_message(data)
            elif message_type == 'hint_request':
                await self.handle_hint_request(data)
            elif message_type == 'struggle_signal':
                await self.handle_struggle_signal(data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
    
    async def handle_chat_message(self, data):
        """
        Handle regular chat messages.
        """
        content = data.get('content', '').strip()
        
        if not content:
            return
        
        # Save to database
        message = await self.save_message(content, 'TEXT')
        
        # Check for off-topic content
        is_moderated = await self.check_moderation(content)
        
        # Detect struggle signals
        if await self.detect_struggle(content):
            await self.handle_struggle_detected(content)
        
        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'sender': self.user.username,
                    'sender_id': self.user.id,
                    'content': content,
                    'is_moderated': is_moderated,
                    'created_at': message.created_at.isoformat()
                }
            }
        )
    
    async def handle_hint_request(self, data):
        """
        Handle AI hint requests (3-stage Socratic system).
        """
        question = data.get('question', '')
        topic = data.get('topic', '')
        
        if not question or not topic:
            return
        
        # Create hint request
        hint_request = await self.create_hint_request(question, topic)
        
        # Generate hint using AI
        hint_text = await self.generate_hint(question, topic, stage=1)
        
        # Save hint
        await self.save_hint(hint_request, hint_text, stage=1)
        
        # Send hint to user
        await self.send(text_data=json.dumps({
            'type': 'hint',
            'hint_id': hint_request.id,
            'stage': 1,
            'hint': hint_text,
            'question': question,
            'topic': topic
        }))
    
    async def handle_struggle_signal(self, data):
        """
        Handle struggle signals and initiate peer matching.
        """
        topic = data.get('topic', '')
        signal = data.get('signal', '')
        
        if not topic or not signal:
            return
        
        # Record struggle
        struggle = await self.record_struggle(topic, signal)
        
        # Find matching peer
        peer = await self.find_peer_match(topic)
        
        if peer:
            # Notify peer about struggling student
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'peer_match_suggestion',
                    'struggling_student': self.user.username,
                    'helping_peer': peer.username,
                    'topic': topic
                }
            )
    
    # Group send handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))
    
    async def user_join(self, event):
        """Send user join notification."""
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def user_leave(self, event):
        """Send user leave notification."""
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'username': event['username'],
            'user_id': event['user_id']
        }))
    
    async def peer_match_suggestion(self, event):
        """Send peer match suggestion."""
        await self.send(text_data=json.dumps({
            'type': 'peer_match_suggestion',
            'struggling_student': event['struggling_student'],
            'helping_peer': event['helping_peer'],
            'topic': event['topic']
        }))
    
    # Database operations
    @database_sync_to_async
    def mark_user_active(self):
        try:
            room = StudyRoom.objects.get(id=self.room_id)
            member, _ = RoomMember.objects.get_or_create(
                room=room,
                user=self.user,
                defaults={'is_active': True}
            )
            member.is_active = True
            member.save()
        except StudyRoom.DoesNotExist:
            pass
    
    @database_sync_to_async
    def mark_user_inactive(self):
        try:
            room = StudyRoom.objects.get(id=self.room_id)
            member = RoomMember.objects.get(room=room, user=self.user)
            member.is_active = False
            member.save()
        except (StudyRoom.DoesNotExist, RoomMember.DoesNotExist):
            pass
    
    @database_sync_to_async
    def save_message(self, content, message_type):
        room = StudyRoom.objects.get(id=self.room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=content,
            message_type=message_type
        )
    
    @database_sync_to_async
    def create_hint_request(self, question, topic):
        room = StudyRoom.objects.get(id=self.room_id)
        return HintRequest.objects.create(
            room=room,
            student=self.user,
            question=question,
            topic=topic
        )
    
    @database_sync_to_async
    def check_moderation(self, content):
        """
        Check for off-topic content using NLP.
        Integration with moderation service will be implemented.
        """
        # Placeholder for NLP-based moderation
        return False
    
    @database_sync_to_async
    def detect_struggle(self, content):
        """
        Detect struggle signals from message content.
        Integration with struggle detection service will be implemented.
        """
        # Placeholder for struggle detection
        struggle_keywords = ['confused', 'stuck', 'help', 'dont understand', 'lost']
        return any(keyword in content.lower() for keyword in struggle_keywords)
    
    @database_sync_to_async
    def record_struggle(self, topic, signal):
        room = StudyRoom.objects.get(id=self.room_id)
        return StruggleDetection.objects.create(
            room=room,
            student=self.user,
            topic=topic,
            struggle_source='MESSAGE',
            struggle_signal=signal,
            severity_score=0.7
        )
    
    async def generate_hint(self, question, topic, stage):
        """
        Generate hint using Claude API.
        Integration with hint engine will be implemented.
        """
        # Placeholder for AI hint generation
        stage_messages = {
            1: f"Think about the key concept of {topic}. What's the first step?",
            2: f"What would happen if you tried...? How does that relate to {topic}?",
            3: f"Here's a partial approach: Start by identifying the pattern in {topic}..."
        }
        return stage_messages.get(stage, "Try breaking down the problem.")
    
    @database_sync_to_async
    def save_hint(self, hint_request, hint_text, stage):
        if stage == 1:
            hint_request.stage_1_hint = hint_text
        elif stage == 2:
            hint_request.stage_2_hint = hint_text
        elif stage == 3:
            hint_request.stage_3_hint = hint_text
        hint_request.current_stage = stage
        hint_request.save()
    
    @database_sync_to_async
    def find_peer_match(self, topic):
        """
        Find a peer who recently solved the same topic to provide help.
        """
        room = StudyRoom.objects.get(id=self.room_id)
        # Placeholder logic - will be enhanced with topic matching
        members = room.members.filter(is_active=True).exclude(user=self.user)
        return members.first().user if members.exists() else None
    
    @database_sync_to_async
    def handle_struggle_detected(self, signal):
        """Handle detected struggle - can trigger notifications, peer matching, etc."""
        pass
