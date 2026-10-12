# Hire Me - AI Interview Simulator Backend

A local-first AI interview simulator and English communication improvement platform backend built with Django.

## Features

### Phase 1 Complete ✅
- ✅ Django REST API with authentication
- ✅ User registration, login, logout
- ✅ Database models for interviews, questions, knowledge base
- ✅ Communication learning log models
- ✅ Practice and progress tracking models
- ✅ Automated tests

### Phase 2 Complete ✅
- ✅ Interview session CRUD operations
- ✅ Interview state management (ready → asking → listening → processing → finished)
- ✅ Pause, resume, finish interview actions
- ✅ Interview turn management with auto-incrementing turn numbers
- ✅ Role and topic management
- ✅ Question bank with filtering by topic, difficulty, and type
- ✅ User isolation (users only see their own interviews)
- ✅ Comprehensive API tests for all endpoints
- ✅ Data seeding command

### Phase 3 Complete ✅
- ✅ Ollama LLM client with connection management
- ✅ Interview orchestrator for question generation
- ✅ Dynamic question generation using LLM
- ✅ Fallback to question bank when LLM unavailable
- ✅ Follow-up question generation based on answers
- ✅ Interview evaluation with LLM scoring
- ✅ Automatic evaluation on interview completion
- ✅ Error handling and timeout management
- ✅ Ollama status check command

### Phase 4 Complete ✅
- ✅ faster-whisper integration for speech-to-text
- ✅ Piper TTS integration for text-to-speech
- ✅ Audio file validation (format, size, duration)
- ✅ Audio format conversion with FFmpeg
- ✅ Transcription with confidence scores and timestamps
- ✅ Text-to-speech caching for efficiency
- ✅ Speech API endpoints (transcribe, synthesize, analyze)
- ✅ Comprehensive error handling
- ✅ Speech services status check command

### Phase 5 Complete ✅
- ✅ Silent communication issue detection during interviews
- ✅ Filler word detection (um, uh, like, you know)
- ✅ Repeated word detection (consecutive and frequent)
- ✅ Grammar issue detection with LLM
- ✅ Speaking rate analysis (words per minute)
- ✅ Pronunciation uncertainty flagging from transcription
- ✅ Issue categorization and confidence scoring
- ✅ Post-interview issue review (never interrupts interview)
- ✅ Issue confirmation/dismissal workflow
- ✅ Communication summary and statistics

### Phase 6 Complete ✅
- ✅ Practice queue with prioritized issues
- ✅ Text-based practice submissions
- ✅ Audio-based practice with automatic transcription
- ✅ Reference audio generation for target pronunciation
- ✅ Automatic practice attempt evaluation and scoring
- ✅ Auto-mastery after 3 successful attempts (score ≥8.0)
- ✅ Manual mastery marking
- ✅ Practice history tracking
- ✅ Comprehensive progress statistics
- ✅ Category-based filtering

### Phase 7 Complete ✅
- ✅ Document import and processing (text, markdown)
- ✅ Text chunking with configurable size and overlap
- ✅ SQLite FTS5-based keyword search
- ✅ Knowledge source management with verification status
- ✅ Answer verification against documentation
- ✅ RAG integration with interview question generation
- ✅ Source attribution and licensing tracking
- ✅ Document statistics and management
- ✅ Admin-only document import control

### Phase 8 Complete ✅
- ✅ Overview report with interview/performance/communication stats
- ✅ Communication improvement report with issue breakdown
- ✅ Interview performance report with score progression
- ✅ Progress snapshot creation for tracking over time
- ✅ Improvement trend analysis (improving/stable/declining)
- ✅ Practice timeline visualization
- ✅ Personalized recommendations based on activity
- ✅ Performance breakdown by topic and difficulty
- ✅ Common pattern analysis
- ✅ User-specific insights generation

## Requirements

- Python 3.11 or 3.12
- SQLite (included with Python)
- Virtual environment support

## Windows Setup Instructions

### 1. Install Python

Ensure Python 3.11 or 3.12 is installed:
```bash
python --version
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update settings:
```bash
copy .env.example .env
```

Edit `.env` and set your `SECRET_KEY`:
```
SECRET_KEY=your-secret-key-here
```

### 5. Database Setup

Run migrations to create the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run Tests

```bash
pytest
```

### 8. Seed Initial Data (Optional)

```bash
python manage.py seed_data
```

This creates sample roles, topics, and questions.

### 9. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/me/` - Get current user

### Roles
- `GET /api/v1/roles/` - List all roles
- `POST /api/v1/roles/` - Create new role
- `GET /api/v1/roles/{id}/` - Get role details
- `PUT /api/v1/roles/{id}/` - Update role
- `DELETE /api/v1/roles/{id}/` - Delete role

### Topics
- `GET /api/v1/topics/` - List all topics (filter by ?difficulty_level=)
- `POST /api/v1/topics/` - Create new topic
- `GET /api/v1/topics/{id}/` - Get topic details
- `PUT /api/v1/topics/{id}/` - Update topic
- `DELETE /api/v1/topics/{id}/` - Delete topic

### Questions
- `GET /api/v1/questions/` - List questions (filter by ?topic=, ?difficulty=, ?question_type=)
- `POST /api/v1/questions/` - Create new question
- `GET /api/v1/questions/{id}/` - Get question details
- `PUT /api/v1/questions/{id}/` - Update question
- `DELETE /api/v1/questions/{id}/` - Delete question

### Interviews
- `GET /api/v1/interviews/` - List user's interviews
- `POST /api/v1/interviews/` - Create new interview
- `GET /api/v1/interviews/{id}/` - Get interview with turns
- `PUT /api/v1/interviews/{id}/` - Update interview
- `DELETE /api/v1/interviews/{id}/` - Delete interview
- `POST /api/v1/interviews/{id}/start/` - Start interview
- `POST /api/v1/interviews/{id}/pause/` - Pause interview
- `POST /api/v1/interviews/{id}/resume/` - Resume interview
- `POST /api/v1/interviews/{id}/finish/` - Finish interview (with optional evaluation)
- `POST /api/v1/interviews/{id}/turns/` - Add turn to interview
- `POST /api/v1/interviews/{id}/next_question/` - Generate next question (LLM or bank)
- `POST /api/v1/interviews/{id}/answer_and_continue/` - Submit answer and get next question
- `GET /api/v1/interviews/{id}/report/` - Get interview evaluation report

### Speech
- `POST /api/v1/speech/transcribe/` - Transcribe audio to text
- `POST /api/v1/speech/synthesize/` - Convert text to speech
- `POST /api/v1/speech/analyze/` - Analyze audio metrics

### Communication Issues
- `GET /api/v1/communication/issues/` - List issues (filter by ?status=, ?category=)
- `POST /api/v1/communication/issues/` - Create issue manually
- `GET /api/v1/communication/issues/{id}/` - Get issue details
- `POST /api/v1/communication/issues/{id}/confirm/` - Confirm issue as valid
- `POST /api/v1/communication/issues/{id}/dismiss/` - Dismiss as false positive
- `POST /api/v1/communication/issues/{id}/start_practicing/` - Mark as practicing
- `POST /api/v1/communication/analyze/{session_id}/` - Analyze session for issues
- `GET /api/v1/communication/summary/` - Get user's issue summary

### Practice Lab
- `GET /api/v1/practice/queue/` - Get practice queue (filter by ?category=, ?limit=)
- `POST /api/v1/practice/submit/` - Submit practice attempt (text or audio)
- `GET /api/v1/practice/history/` - Get practice history (filter by ?issue_id=)
- `GET /api/v1/practice/progress/` - Get overall progress statistics
- `POST /api/v1/practice/issues/{id}/master/` - Mark issue as mastered
- `POST /api/v1/practice/issues/{id}/reference-audio/` - Generate reference audio

### Knowledge Base
- `GET /api/v1/knowledge/sources/` - List knowledge sources
- `POST /api/v1/knowledge/import/` - Import document (admin only)
- `GET /api/v1/knowledge/sources/{id}/` - Get source details
- `GET /api/v1/knowledge/sources/{id}/chunks/` - Get source chunks
- `GET /api/v1/knowledge/sources/{id}/stats/` - Get source statistics
- `POST /api/v1/knowledge/search/` - Search knowledge base
- `POST /api/v1/knowledge/verify/` - Verify answer against sources
- `GET /api/v1/knowledge/list/` - List all verified sources

### Reports
- `GET /api/v1/reports/overview/` - Get comprehensive overview report
- `GET /api/v1/reports/communication/` - Get communication improvement report
- `GET /api/v1/reports/interviews/` - Get interview performance report
- `POST /api/v1/reports/snapshot/` - Create progress snapshot

### Example: Create Interview

```json
POST /api/v1/interviews/
{
    "role": 1,
    "topic": 2,
    "difficulty": "intermediate",
    "interview_type": "technical"
}
```

### Example: LLM Question Generation

```json
POST /api/v1/interviews/1/next_question/
{
    "use_llm": true
}

Response:
{
    "question": "Can you explain the difference between a list and a tuple in Python?",
    "turn_number": 2
}
```

### Example: Answer and Get Next Question

```json
POST /api/v1/interviews/1/answer_and_continue/
{
    "question_text": "What is a Python decorator?",
    "answer_text": "A decorator is a function that wraps another function to modify its behavior"
}

Response:
{
    "turn_number": 1,
    "next_question": "Can you provide an example of using a decorator?",
    "can_continue": true
}
```

### Example: Text-to-Speech

```json
POST /api/v1/speech/synthesize/
{
    "text": "Hello, this is a test of the text to speech system."
}

Response:
{
    "audio_url": "/media/audio/tts/abc123.wav",
    "text": "Hello, this is a test..."
}
```

### Example: Speech-to-Text

```bash
curl -X POST http://localhost:8000/api/v1/speech/transcribe/ \
  -H "Authorization: Session" \
  -F "audio=@interview_answer.wav" \
  -F "language=en"

Response:
{
    "text": "Python is a high-level programming language...",
    "language": "en",
    "confidence": 0.95,
    "duration": 15.3,
    "segments": [...]
}
```

```json
POST /api/v1/interviews/1/finish/
{
    "generate_evaluation": true
}

Response:
{
    "id": 1,
    "status": "finished",
    "evaluation": {
        "technical_score": 8.5,
        "completeness_score": 7.5,
        "reasoning_score": 8.0,
        "organization_score": 7.0,
        "overall_feedback": "Strong technical understanding...",
        "strengths": "- Clear explanations\n- Good examples",
        "improvements": "- Could expand on edge cases"
    }
}
```

### Example: Overview Report

```json
GET /api/v1/reports/overview/

Response:
{
    "user": {"username": "testuser", "email": "test@example.com"},
    "interviews": {
        "total": 15,
        "finished": 12,
        "recent_30d": 5,
        "completion_rate": 80.0
    },
    "performance": {
        "average_scores": {
            "technical": 8.2,
            "completeness": 7.5,
            "reasoning": 7.8,
            "organization": 7.3
        },
        "evaluations_count": 12
    },
    "communication": {
        "total_issues": 25,
        "mastered": 15,
        "mastery_rate": 60.0
    },
    "practice": {"total_attempts": 48, "recent_30d": 12},
    "improvement_trend": "improving"
}
```

### Example: Create Progress Snapshot

```json
POST /api/v1/reports/snapshot/

Response:
{
    "id": 5,
    "date": "2024-01-15",
    "total_issues": 25,
    "mastered_issues": 15,
    "message": "Snapshot created successfully"
}
```

## Project Structure

```
backend/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── accounts/         # User authentication
│   ├── interviews/       # Interview sessions and turns
│   ├── questions/        # Interview questions
│   ├── knowledge/        # RAG knowledge base
│   ├── speech/           # Speech processing
│   ├── communication/    # Learning issues
│   ├── practice/         # Practice attempts
│   └── reports/          # Progress reports
├── tests/
│   ├── test_auth.py
│   └── test_models.py
└── requirements.txt
```

## Development Phases

- ✅ **Phase 1**: Project setup, authentication, database models (COMPLETE)
- ✅ **Phase 2**: Interview session management, questions, state transitions (COMPLETE)
- ✅ **Phase 3**: Local LLM integration (Ollama) (COMPLETE)
- ✅ **Phase 4**: Speech-to-text and text-to-speech (COMPLETE)
- ✅ **Phase 5**: Communication issue logging (COMPLETE)
- ✅ **Phase 6**: English Improvement Lab (COMPLETE)
- ✅ **Phase 7**: RAG knowledge base (COMPLETE)
- ✅ **Phase 8**: Reports and documentation (COMPLETE)

## Additional Dependencies (Future Phases)

### Ollama (Phase 3)
Download and install from: https://ollama.ai/

```bash
# Windows: Download installer from website

# Start Ollama service
ollama serve

# Pull a model (recommended for CPU)
ollama pull llama3.2:3b

# Or use a smaller model
ollama pull llama3.2:1b

# Verify
python manage.py check_ollama
```

### FFmpeg (Phase 4)
Download from: https://ffmpeg.org/download.html

```bash
# Windows: Download zip, extract, add to PATH

# Verify
ffmpeg -version
```

### Faster Whisper (Phase 4)
Already in requirements.txt

```bash
pip install faster-whisper

# Models auto-download on first use
# Check: python manage.py check_speech
```

### Piper TTS (Phase 4)
Already in requirements.txt

```bash
pip install piper-tts

# Voices auto-download on first use
# Check: python manage.py check_speech
```

## Admin Interface

Access at `http://localhost:8000/admin/` after creating a superuser.

## Testing

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_interviews.py
pytest tests/test_questions.py
```

Run with coverage:
```bash
pytest --cov
```

Manual API testing:
```bash
# Phase 2
python test_phase2_api.py

# Phase 3 (requires Ollama running)
python test_phase3_api.py

# Phase 4 (requires speech services)
python test_phase4_api.py

# Phase 5 (communication issues)
python test_phase5_api.py

# Phase 6 (practice lab)
python test_phase6_api.py

# Phase 7 (RAG knowledge base)
python test_phase7_api.py

# Phase 8 (reports)
python test_phase8_api.py
```

Management commands:
```bash
# Check Ollama
python manage.py check_ollama

# Check Speech services
python manage.py check_speech

# Analyze interviews for issues
python manage.py analyze_interviews --all

# Import documentation
python manage.py import_docs --file path/to/doc.txt --title "Python Docs" --url "https://docs.python.org"
```

## Security Notes

- Never commit `.env` files
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Audio files are stored locally in `media/`
- User data is isolated by authentication

## License

Private project for learning purposes.
