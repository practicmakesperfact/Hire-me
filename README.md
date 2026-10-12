# Hire Me - AI Interview Simulator Backend

A local-first AI interview simulator and English communication improvement platform backend built with Django.

## Features (Phase 1 Complete)

- ✅ Django REST API with authentication
- ✅ User registration, login, logout
- ✅ Database models for interviews, questions, knowledge base
- ✅ Communication learning log models
- ✅ Practice and progress tracking models
- ✅ Automated tests

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

### 8. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints (Phase 1)

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/me/` - Get current user

### Example Registration Request

```json
POST /api/v1/auth/register/
{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### Example Login Request

```json
POST /api/v1/auth/login/
{
    "username": "john",
    "password": "securepass123"
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
- ⏳ **Phase 2**: Interview session management
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

Run with coverage:
```bash
pytest --cov
```

## Security Notes

- Never commit `.env` files
- Change `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Audio files are stored locally in `media/`
- User data is isolated by authentication

## License

Private project for learning purposes.
