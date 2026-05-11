# StudySync - AI-Powered Collaborative Study Platform

## 🎯 Project Overview

StudySync is a real-time AI-powered collaborative study platform designed for college students. Students join topic-based study rooms (DSA, Aptitude, Mock Tests), study together, and receive intelligent guidance through an advanced AI hint engine—never just answers.

## ✨ Core Features

### 1. Topic-Based Study Rooms
- Real-time chat with max 6 students per room
- Topic categorization (DSA, Aptitude, Mock Tests, etc.)
- Active member tracking with online status
- Room capacity management

### 2. Pomodoro Timer & Streak Tracking
- 45-minute study sessions / 10-minute breaks
- Streak tracking across multiple sessions
- Session performance analytics

### 3. AI Hint Engine (3-Stage Socratic System)
- **Stage 1**: Conceptual guidance without spoilers
- **Stage 2**: Directed questions to guide thinking
- **Stage 3**: Partial solutions with explanation
- Never provides direct answers

### 4. Real-Time Struggle Detection
- NLP-based confusion detection from messages
- Automatic peer matching: connects struggling students with those who just solved the same topic
- Peer learning facilitation

### 5. NLP-Based Off-Topic Moderation
- Context-aware moderation (not just keyword blocking)
- Maintains focused learning environment
- Automatic flagging of off-topic messages

### 6. Room Intelligence
- Session summaries with key learnings
- Weak topic detection per student
- Next topic suggestions based on performance
- Learning path recommendations

### 7. Personal Knowledge Graph
- Mastery level tracking per topic
- Learning velocity calculation
- Placement readiness score
- Progress visualization

## 🛠️ Tech Stack

### Frontend
- **React** - UI framework
- **Tailwind CSS** - Styling
- **WebSocket Client** - Real-time communication
- **Deployment**: Vercel

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - REST API
- **Django Channels** - WebSocket support
- **Redis** - Message broker for Channels
- **Deployment**: Railway

### AI & NLP Layer
- **Claude API** - Intelligent hint generation
- **LangChain** - LLM orchestration
- **sentence-transformers** - Topic classification & similarity
- **ChromaDB** - Vector database for embeddings

### Database
- **PostgreSQL** - Primary database (via Supabase)
- **Redis** - Caching & Channels broker

### DevOps & CI/CD
- **GitHub Actions** - Auto-deploy on push
- **Vercel** - Frontend deployment
- **Railway** - Backend deployment

## 📦 Project Structure

```
studysync/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── studysync/
│   │   ├── settings.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── urls.py
│   │   └── routing.py
│   ├── rooms/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── chat/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── consumers.py
│   │   └── urls.py
│   ├── ai/
│   │   ├── hint_engine.py
│   │   ├── moderation.py
│   │   ├── struggle_detection.py
│   │   └── topic_classifier.py
│   └── utils/
│       └── helpers.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.js
│   └── package.json
└── .github/
    └── workflows/
        └── deploy.yml
```

## 🚀 Quick Start

### Backend Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Pooja0726/StudySync.git
   cd StudySync/backend
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   # Terminal 1: Django development server
   python manage.py runserver
   
   # Terminal 2: Redis server (for WebSockets)
   redis-server
   
   # Terminal 3: Daphne (ASGI server for WebSockets)
   daphne -b 0.0.0.0 -p 8001 studysync.asgi:application
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

## 📚 API Endpoints

### Study Rooms
- `GET /api/rooms/` - List all rooms
- `POST /api/rooms/` - Create new room
- `GET /api/rooms/{id}/` - Room details
- `POST /api/rooms/{id}/join/` - Join room
- `POST /api/rooms/{id}/leave/` - Leave room
- `GET /api/rooms/{id}/members/` - Room members
- `GET /api/rooms/{id}/session-summary/` - Session intelligence

### Chat & Messages
- `GET /api/chat/messages/` - Message history
- `POST /api/chat/messages/` - Send message
- `GET /api/chat/hints/` - Hint history
- `POST /api/chat/hints/` - Request hint

### Knowledge Graph
- `GET /api/knowledge-graph/` - Personal progress
- `GET /api/knowledge-graph/topics/` - Topic mastery
- `GET /api/knowledge-graph/readiness-score/` - Placement readiness

## 🤖 AI Features

### Hint Engine
```python
from ai.hint_engine import HintEngine

engine = HintEngine()
hint = engine.generate_hint(
    topic="Binary Search",
    question="Find first occurrence in sorted array",
    stage=1  # 1, 2, or 3
)
```

### Topic Classification
```python
from ai.topic_classifier import TopicClassifier

classifier = TopicClassifier()
topic = classifier.classify("How to optimize merge sort for linked lists?")
```

### Struggle Detection
```python
from ai.struggle_detection import StruggleDetector

detector = StruggleDetector()
is_struggling = detector.detect("I'm so confused with dynamic programming")
```

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/studysync

# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Services
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-key (optional)

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# WebSocket
CHANNEL_LAYERS_BACKEND=channels_redis.core.RedisChannelLayer
```

## 📊 Database Models

### Study Room
```python
class StudyRoom(models.Model):
    topic = models.CharField(max_length=100)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    max_members = models.IntegerField(default=6)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Knowledge Graph
```python
class KnowledgeGraph(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    topics_mastered = models.JSONField(default=dict)
    learning_velocity = models.FloatField(default=0.0)
    placement_readiness_score = models.FloatField(default=0.0)
    current_streak = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific test
python manage.py test rooms.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📈 Performance Optimization

- Database query optimization with `select_related()` and `prefetch_related()`
- Redis caching for frequently accessed data
- Celery tasks for async operations (email notifications, summaries)
- WebSocket connection pooling
- Vector similarity search optimization in ChromaDB

## 🚢 Deployment

### Railway (Backend)

1. Connect your GitHub repo to Railway
2. Set environment variables in Railway dashboard
3. Railway auto-deploys on every push to main

### Vercel (Frontend)

1. Connect your GitHub repo to Vercel
2. Set build command: `npm run build`
3. Set output directory: `build`
4. Vercel auto-deploys on every push to main

## 📝 Contributing

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👥 Support

For issues or questions, please open a GitHub issue or contact the team.

---

**Made with ❤️ for collaborative learning**
