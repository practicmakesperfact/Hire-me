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
- `POST /api/v1/interviews/{id}/finish/` - Finish interview
- `POST /api/v1/interviews/{id}/turns/` - Add turn to interview

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

### Example: Start Interview and Add Turn

```json
POST /api/v1/interviews/1/start/
```

```json
POST /api/v1/interviews/1/turns/
{
    "question_text": "What is a Python decorator?",
    "answer_text": "A function that wraps another function to modify its behavior"
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
- ⏳ **Phase 3**: Local LLM integration (Ollama)
- ⏳ **Phase 4**: Speech-to-text and text-to-speech
- ⏳ **Phase 5**: Communication issue logging
- ⏳ **Phase 6**: English Improvement Lab
- ⏳ **Phase 7**: RAG knowledge base
- ⏳ **Phase 8**: Reports and documentation

## Additional Dependencies (Future Phases)

### Ollama (Phase 3)
Download and install from: https://ollama.ai/
```bash
ollama pull llama3.2:3b
```

### FFmpeg (Phase 4)
Download from: https://ffmpeg.org/download.html
Add to PATH.

### Faster Whisper (Phase 4)
Will be installed via requirements.txt in Phase 4.

### Piper TTS (Phase 4)
Installation instructions will be provided in Phase 4.

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
python test_phase2_api.py
```

## Security Notes

- Never commit `.env` files
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Audio files are stored locally in `media/`
- User data is isolated by authentication

## License

Private project for learning purposes.
