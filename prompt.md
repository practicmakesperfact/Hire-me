# HIRE ME — Backend Development Prompt

## 1. Project Overview

Build a production-minded, modular backend for **Hire Me**, a local-first AI interview simulator and English communication improvement platform.

The application has two core modes:

1. **Interview Simulator:** Conduct realistic technical and behavioral interviews using voice or text. The interviewer must never interrupt the user to correct pronunciation, grammar, vocabulary, or communication mistakes.
2. **English Improvement Lab:** After an interview, allow users to review recorded learning insights, practise difficult words and sentences, improve pronunciation and fluency, and track progress over time.

The system must run locally on Windows 10 with an Intel i5 10th-generation CPU, 16 GB RAM, and no dedicated GPU.

## 2. Mandatory Constraints

- No paid AI APIs or mandatory cloud services.
- No OpenAI, Anthropic, Gemini, or other paid hosted LLM API dependencies.
- Use locally running AI models.
- Store application data in SQLite initially.
- Store uploaded or recorded audio locally and minimize audio retention.
- Keep secrets and personal data out of Git.
- Support offline operation after all required models and dependencies are downloaded.
- Do not implement frontend functionality in this task.
- Do not duplicate backend features that already exist. Inspect the repository before making changes.
- Use Python 3.11 or 3.12 if compatible with the existing project and speech-processing dependencies.
- Prioritize reliability, clear architecture, low resource usage, and maintainable code.

## 3. Technology Stack

- Python
- Django
- Django REST Framework
- SQLite
- Django ORM and Django migrations
- Ollama for local LLM inference
- faster-whisper for speech-to-text
- A local text-to-speech engine, such as Piper or a maintained compatible alternative
- FFmpeg for audio conversion when required
- Local audio-analysis libraries for speech metrics
- pytest and pytest-django for testing
- Pydantic for structured validation where useful

Use a local embedding model and vector index only when necessary. Begin with SQLite FTS5 or another simple local retrieval mechanism if suitable.

Do not install heavyweight dependencies without explaining why they are necessary.

## 4. Repository Inspection

Before implementation:

1. Inspect the current directory structure and existing files.
2. Identify existing Django applications, dependencies, database models, API routes, and tests.
3. Reuse existing working code where appropriate.
4. Create a concise implementation plan.
5. Identify missing features and potential dependency conflicts.
6. Implement incrementally without unnecessarily rewriting the project.

If the repository is empty, initialize the backend with a clean Django project structure.

## 5. Suggested Architecture

Use a modular structure similar to:

backend/
  manage.py
  config/
    settings.py
    urls.py
    asgi.py
  apps/
    accounts/
    interviews/
    questions/
    knowledge/
    speech/
    communication/
    practice/
    reports/
  services/
    llm/
    rag/
    speech_to_text/
    text_to_speech/
    audio_analysis/
    evaluation/
  tests/
  requirements.txt
  .env.example
  .gitignore
  README.md

Adapt this structure if a simpler organization better fits the existing repository. Avoid unnecessary abstractions and circular dependencies.

## 6. Authentication and User Management

Implement Django authentication with:

- User registration and login.
- Logout.
- Current-user profile endpoint.
- Secure password hashing.
- User-specific interview sessions and learning records.
- Authorization checks for every private resource.
- Optional local development authentication configuration.

Never expose one user's interview records or audio to another user.

Use session authentication or JWT where appropriate. Do not store plaintext passwords or hardcode secrets.

## 7. Interview Management

Create models and APIs for:

- Interview roles and job descriptions.
- Interview topics and difficulty levels.
- Technical and behavioral questions.
- Interview sessions.
- Interview turns.
- Interview evaluations and reports.

Support interview types such as:

- Software engineering fundamentals.
- Python and Django.
- React and frontend development.
- Databases and SQL.
- Data structures and algorithms.
- Machine learning and AI.
- Behavioral and HR interviews.
- Custom user-provided topics.

Each interview session should support these states:

READY → ASKING → LISTENING → TRANSCRIBING → PROCESSING → ASKING → FINISHED

Support pause, resume, cancellation, and recovery from recoverable errors.

Every interview turn should preserve the question, the user's original transcript, timestamps, and associated evaluation records.

## 8. Interview Orchestrator

Implement a dedicated interview orchestration service.

Responsibilities:

1. Select or generate an interview question.
2. Use approved knowledge sources when generating technical questions.
3. Deliver the question as text and optionally local synthesized audio.
4. Accept the user's spoken or typed answer.
5. Transcribe audio locally when needed.
6. Generate a follow-up question based on the answer.
7. Save the conversation and relevant evidence.
8. Produce a report when the session finishes.

The interviewer must not interrupt an answer to correct English.

During the interview, do not display or speak grammar corrections, pronunciation warnings, or vocabulary suggestions. Collect learning insights in the background or derive them after the turn has been stored.

Interview performance evaluation must be separate from English-learning analysis.

## 9. Local LLM Integration

Implement an Ollama client service that connects to a locally configured Ollama instance.

Requirements:

- Configure the Ollama base URL and model name using environment variables.
- Set configurable request timeouts.
- Handle unavailable models, connection failures, invalid responses, and inference errors.
- Validate structured outputs before saving them.
- Use JSON or schema-constrained outputs when supported.
- Support a fallback message when the model is unavailable.
- Avoid repeatedly loading or switching heavyweight models.
- Never send user data to a hosted LLM provider.

Do not hardcode a specific model. Make it configurable so a small quantized instruction model can be used on CPU.

## 10. Local RAG Knowledge Base

Implement a retrieval-augmented generation service for interview questions and feedback.

Start with approved, locally stored technical documentation, such as:

- Official Python documentation.
- Official Django documentation.
- Official React documentation.
- Official PostgreSQL documentation.
- Official scikit-learn documentation.

Add licensed interview question banks only when their reuse permissions are verified.

Store source metadata including:

- Source title.
- Source URL.
- License or usage permissions.
- Version or publication date when available.
- Import date.
- Verification status.
- Content hash.
- Associated document chunks.

Requirements:

- Import and process supported documents safely.
- Split content into manageable chunks.
- Retrieve relevant passages for questions and evaluations.
- Preserve source attribution.
- Provide citations only when a retrieved source actually supports the claim.
- Never invent citations or claim that a source verifies unsupported information.
- Provide a basic search endpoint.
- Keep document processing local.

Begin with SQLite FTS5 if available and suitable. Add local embeddings and a vector index as a separate, optional enhancement.

## 11. Voice and Speech Processing

Implement separate services for speech-to-text, text-to-speech, and audio analysis.

### Speech-to-text

Use faster-whisper locally.

Requirements:

- Accept supported audio formats.
- Validate file size, duration, and content type.
- Convert unsupported formats using FFmpeg when available.
- Return the recognized transcript and available timing information.
- Record transcription confidence information when supported.
- Flag uncertain segments for review.
- Never assume a transcription error proves that the user pronounced a word incorrectly.

### Text-to-speech

Use a locally installed TTS engine.

Requirements:

- Convert interviewer questions into speech.
- Allow configurable voice and speech rate when supported.
- Cache reusable generated prompts where appropriate.
- Save generated audio locally only when necessary.
- Provide clear errors when a required voice model is unavailable.

### Audio analysis

Extract useful, explainable measurements where technically supported:

- Speaking rate in words per minute.
- Pause duration and frequency.
- Silence ratio.
- Filler-word frequency.
- Repeated words and phrases.
- Approximate volume consistency.
- Basic pitch and vocal-variation measurements.

Do not treat pitch, accent, or a particular speaking style as proof of professionalism or communication ability.

Clearly distinguish objective measurements, estimates, and AI-generated interpretations.

## 12. Silent Communication Learning Log

This is a core feature.

During an interview, record potential learning issues without interrupting the user.

Create a CommunicationIssue model with fields such as:

- User.
- Interview session.
- Interview turn.
- Issue category.
- Original text or word.
- Proposed correction.
- Explanation.
- Supporting evidence.
- Confidence score, where available.
- Review status.
- Practice count.
- Mastery status.
- Created timestamp.

Supported categories:

- Potential pronunciation issue.
- Possible speech-recognition error.
- Grammar issue.
- Vocabulary improvement.
- Filler words.
- Repeated words.
- Speaking-rate observation.
- Pause or fluency observation.
- Sentence clarity.
- Answer organization.

Use explicit statuses such as:

- NEEDS_REVIEW
- CONFIRMED
- DISMISSED
- PRACTICING
- MASTERED

Do not automatically classify every uncertain word as a user error.

For suspected pronunciation issues, preserve the original audio segment when available and permitted. Store a reference pronunciation or phoneme-level assessment only when a suitable model supports it.

For grammar and vocabulary issues, preserve the original sentence and the proposed alternative.

All corrections are private learning records. They must never change the original interview transcript or the interview conversation.

Allow users to dismiss false positives and mark corrections as useful or incorrect.

## 13. English Improvement Lab

Build backend functionality that allows users to practise mistakes from previous interviews.

Required capabilities:

- List learning issues by category.
- Filter by interview, date, status, and difficulty.
- Retrieve the original word or sentence.
- Show the proposed correction and explanation.
- Play an available original audio segment.
- Generate or retrieve local reference audio.
- Record a new practice attempt.
- Transcribe the attempt locally.
- Compare the attempt with the target text.
- Return useful pronunciation or fluency feedback when supported.
- Track practice history.
- Mark issues as mastered or needing further practice.
- Recommend the next items to practise.

For grammar exercises, let the user compare the original sentence with a corrected version and then practise speaking the improved sentence.

For pronunciation exercises, use a suitable phoneme-level model where feasible. Do not claim that faster-whisper alone provides reliable phoneme-level pronunciation scoring.

Use a configurable, transparent assessment rubric. Explain uncertainty and avoid presenting estimates as objective truth.

## 14. Progress Tracking and Reports

Create endpoints and services for:

- Interview history.
- Interview performance summaries.
- Communication improvement history.
- Common grammar patterns.
- Frequently flagged words.
- Filler-word trends.
- Speaking-rate trends.
- Practice completion.
- Mastered versus outstanding issues.
- Progress between practice sessions.

Keep technical interview scores separate from communication-practice metrics.

Use consistent scoring rubrics for technical accuracy, completeness, reasoning, and answer organization.

For communication, assess clarity, structure, grammar, vocabulary, fluency, and pronunciation where the available evidence supports the assessment.

Do not calculate misleading scores when insufficient data exists.

## 15. Suggested REST API

Use `/api/v1/` and Django REST Framework.

### Authentication

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`

### Interview configuration

- `GET /api/v1/roles/`
- `POST /api/v1/roles/`
- `GET /api/v1/topics/`
- `GET /api/v1/questions/`

### Interview sessions

- `GET /api/v1/interviews/`
- `POST /api/v1/interviews/`
- `GET /api/v1/interviews/{id}/`
- `POST /api/v1/interviews/{id}/start/`
- `POST /api/v1/interviews/{id}/turns/`
- `POST /api/v1/interviews/{id}/pause/`
- `POST /api/v1/interviews/{id}/resume/`
- `POST /api/v1/interviews/{id}/finish/`
- `GET /api/v1/interviews/{id}/report/`

### Speech

- `POST /api/v1/speech/transcribe/`
- `POST /api/v1/speech/synthesize/`
- `POST /api/v1/speech/analyze/`

### Learning issues

- `GET /api/v1/communication/issues/`
- `GET /api/v1/communication/issues/{id}/`
- `PATCH /api/v1/communication/issues/{id}/`
- `POST /api/v1/communication/issues/{id}/dismiss/`
- `POST /api/v1/communication/issues/{id}/confirm/`

### English practice

- `GET /api/v1/practice/queue/`
- `POST /api/v1/practice/attempts/`
- `GET /api/v1/practice/history/`
- `POST /api/v1/practice/issues/{id}/master/`
- `GET /api/v1/practice/progress/`

### Knowledge base

- `GET /api/v1/knowledge/sources/`
- `POST /api/v1/knowledge/sources/import/`
- `GET /api/v1/knowledge/search/`

### Dashboard

- `GET /api/v1/reports/overview/`
- `GET /api/v1/reports/communication/`
- `GET /api/v1/reports/interviews/`

Adapt these endpoints when a more consistent REST design is appropriate. Use pagination, validation, suitable HTTP status codes, and a consistent error-response structure.

## 16. Database Design

Create appropriate Django models and migrations for:

- User.
- Role.
- Topic.
- Question.
- KnowledgeSource.
- DocumentChunk.
- InterviewSession.
- InterviewTurn.
- InterviewEvaluation.
- CommunicationIssue.
- PracticeAttempt.
- ProgressSnapshot or equivalent aggregated progress records.

Use foreign keys, indexes, uniqueness constraints, and timestamps appropriately.

Avoid storing duplicate data unnecessarily. Preserve immutable snapshots of interview questions and original transcripts where required for historical accuracy.

## 17. Privacy and Security

- Keep all processing local by default.
- Use environment variables for secrets and configurable service addresses.
- Restrict access to private resources by user.
- Validate uploaded audio files and apply configurable upload limits.
- Prevent path traversal and unsafe file access.
- Avoid logging raw transcripts, credentials, or full audio content unnecessarily.
- Provide a way to delete interviews, learning records, and associated audio.
- Delete temporary audio files after processing when retention is unnecessary.
- Configure local services to bind to localhost by default.
- Do not expose Django debug mode or development servers to public networks.
- Include CSRF protection, suitable authentication controls, and secure file handling.
- Document any dependency that may make a network request.

## 18. Testing Requirements

Write automated tests for:

- Registration, login, and permissions.
- Interview creation and state transitions.
- Saving turns and preserving original transcripts.
- Ensuring interview corrections are never spoken or shown mid-interview.
- Creating and reviewing communication issues.
- Correctly separating transcription uncertainty from confirmed learning issues.
- Practice attempts and progress tracking.
- User data isolation.
- File validation and cleanup.
- Ollama-unavailable behavior.
- RAG retrieval and source attribution.
- API validation and error handling.

Mock the LLM, speech models, and TTS engine in ordinary unit tests so the test suite does not require downloading large models or running Ollama.

Provide optional integration tests for real local models.

## 19. Development Phases

Implement in this order:

Phase 1: Project setup, configuration, authentication, database models, and migrations.

Phase 2: Interview session management, questions, turns, and state transitions.

Phase 3: Local Ollama integration and interview orchestration.

Phase 4: Local speech-to-text and text-to-speech integration.

Phase 5: Silent communication issue logging and post-interview evaluation.

Phase 6: English Improvement Lab, practice attempts, and progress tracking.

Phase 7: Local RAG ingestion, retrieval, and source attribution.

Phase 8: Reports, privacy controls, automated testing, and documentation.

Complete and verify each phase before proceeding. Do not generate a large amount of untested code in one step.

## 20. Required Deliverables

When implementation is complete, provide:

1. Working Django backend source code.
2. Database models and migrations.
3. REST API endpoints.
4. Automated tests and their results.
5. `requirements.txt` with compatible dependency versions.
6. `.env.example`.
7. `.gitignore`.
8. README with Windows setup instructions.
9. Instructions for installing and configuring Ollama, faster-whisper, FFmpeg, and the chosen local TTS engine.
10. Commands to create the virtual environment, migrate the database, run tests, and start the server.
11. API endpoint documentation with example requests and responses.
12. A clear list of implemented, partially implemented, and deferred features.

Start by inspecting the existing repository. Then implement Phase 1, run its tests, and report exactly what works before continuing. Do not claim a feature is complete unless it is implemented and verified.