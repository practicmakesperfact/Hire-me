# HIRE ME — Frontend Development Prompt

## 1. Project Overview

Build a complete, responsive frontend for **Hire Me**, a local-first AI interview simulator and English communication improvement platform.

The application has two main purposes:

1. **Interview Simulator:** Practise technical and behavioral interviews using voice or text, with a realistic AI interviewer that does not interrupt to correct English.
2. **English Improvement Lab:** Review pronunciation difficulties, grammar mistakes, vocabulary improvements, filler words, speaking patterns, and previous practice attempts after interviews.

The frontend must be professional enough for a software engineering portfolio and comfortable for daily personal use.

## 2. Mandatory Technology Stack

Use:

- Next.js with the App Router.
- TypeScript with strict type checking.
- Tailwind CSS.
- shadcn/ui for accessible interface components.
- Lucide icons.
- React Hook Form and Zod for form validation where useful.
- Recharts for progress charts.
- Browser MediaRecorder API for recording microphone audio.
- Fetch API or a small typed API client for Django REST integration.

Use stable, mutually compatible dependency versions.

Do not build the backend in Next.js. Django REST Framework remains the source of truth for users, interviews, learning records, and progress.

## 3. Repository Inspection and Integration

Before writing code:

1. Inspect the existing frontend repository.
2. Inspect the available backend API routes and serializers if the backend repository is accessible.
3. Reuse existing components and working code.
4. Create a clear implementation plan.
5. Identify backend endpoints that are not implemented yet.
6. Do not invent successful API responses or pretend missing endpoints exist.

Use an environment variable such as:

`NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1`

Keep API configuration centralized.

Implement typed API services, loading states, empty states, error handling, authentication handling, and reusable components.

If an endpoint is unavailable, show a useful development message and keep the application usable wherever possible.

## 4. Design Direction

Create a modern, calm, polished SaaS-style interface.

Design principles:

- Clean typography and generous spacing.
- Neutral surfaces with one consistent accent color.
- Excellent contrast and accessible controls.
- Light and dark themes.
- Responsive layouts for desktop, tablet, and mobile.
- Consistent cards, forms, tables, dialogs, and navigation.
- Subtle animations only when they improve usability.
- Clear visual feedback for recording, processing, success, and errors.

Avoid excessive gradients, unnecessary decoration, overcrowded dashboards, and distracting animations.

Use a consistent design system with reusable spacing, typography, colors, radii, and component variants.

## 5. Application Layout

Create a responsive authenticated application shell.

### Desktop sidebar

Include:

- Overview
- Start Interview
- Interview History
- English Improvement Lab
- Pronunciation Practice
- Communication Progress
- Knowledge Sources
- Settings

Show the application logo, active navigation state, user profile, and a collapse option.

### Mobile navigation

Use a responsive drawer or mobile navigation pattern. Ensure microphone controls, interview actions, and practice buttons remain easy to reach.

### Global header

Include:

- Current page title.
- Breadcrumbs when useful.
- Theme toggle.
- User profile menu.
- Optional system status for local AI services.

Display service availability only when the frontend has actually checked the backend health endpoint.

## 6. Authentication Pages

Implement:

- Registration.
- Login.
- Logout.
- Current-user profile.
- Form validation.
- Password visibility toggle.
- Loading and error states.
- Protected application routes.

Follow the authentication method implemented by Django.

For session authentication, handle CSRF correctly. If JWT is used, follow the backend's configured token-storage and refresh strategy. Do not expose secrets or hardcode credentials.

## 7. Dashboard

Build a useful dashboard with:

### Summary cards

- Interviews completed.
- Total practice sessions.
- Learning issues awaiting review.
- Words or sentences mastered.

### Progress visualizations

- Communication progress over time.
- Speaking rate over recent sessions.
- Filler-word frequency over time.
- Practice completion.
- Interview performance trends.

### Recent activity

Show recent interviews, recently reviewed mistakes, and suggested practice items.

### Quick actions

- Start a technical interview.
- Start a behavioral interview.
- Continue English practice.
- Review recent communication issues.

Use real backend data. Clearly show loading, no-data, and failure states. Do not fabricate statistics.

## 8. Interview Setup Page

Let users configure:

- Interview type.
- Target role.
- Technical topic.
- Difficulty.
- Interview duration.
- Number of questions, when supported.
- Voice or text interaction.
- Optional job description.
- Optional custom interview instructions.

Provide a microphone and audio-system check before starting a voice interview.

Display the selected configuration and a clear Start Interview action.

Validate required fields and submit the configuration to Django.

## 9. Live Interview Interface

This is a core feature.

Design a focused interview workspace with:

### Main interview area

- Current interviewer question.
- Interviewer audio playback.
- Question number and session progress.
- Text transcript of the conversation.
- Microphone recording status.
- Recording duration.
- Audio-processing status.
- Text-answer fallback.
- Submit answer, pause, resume, and finish actions.

### Voice interaction

Use the browser MediaRecorder API to capture microphone input.

Requirements:

- Request microphone permission only when needed.
- Display clear recording and permission indicators.
- Record audio in a format supported by the backend or convert it through an explicitly supported mechanism.
- Upload audio to the configured Django endpoint.
- Handle unsupported MIME types.
- Handle microphone denial, missing devices, upload failures, and recording errors.
- Prevent accidental duplicate submissions.
- Stop microphone tracks when recording ends or the page is left.
- Do not claim that an answer was submitted or processed until the backend confirms it.

Play generated interviewer audio returned by Django.

Provide keyboard-accessible controls and a text-answer fallback.

### Non-interruption requirement

The interview UI must not display pronunciation corrections, grammar suggestions, vocabulary replacements, or English-learning warnings while the interview is in progress.

The user should be able to focus on answering naturally.

Store and display interview questions and answers independently of the English Improvement Lab.

## 10. Interview Results Page

After an interview is finished, show a structured report containing:

- Overall interview summary.
- Technical accuracy.
- Answer completeness.
- Reasoning quality.
- Answer organization.
- Strong answers.
- Areas for improvement.
- Recommended technical topics to practise.
- Communication-learning items discovered during the interview.

Clearly separate interview performance from English communication metrics.

Include actions to:

- Review the transcript.
- Revisit a question.
- Start another interview.
- Open flagged communication issues in the English Improvement Lab.

Do not display unsupported scores. Explain the rubric when scores are available.

## 11. English Improvement Lab

This is the second core feature.

Create a dedicated learning workspace where users review mistakes collected from past interviews.

### Overview

Display:

- Issues needing review.
- Confirmed learning issues.
- Items currently being practised.
- Mastered items.
- Recent practice activity.

### Issue categories

Support filters for:

- Pronunciation.
- Possible transcription errors.
- Grammar.
- Vocabulary.
- Filler words.
- Repeated words.
- Speaking rate.
- Pauses and fluency.
- Sentence clarity.
- Answer organization.

### Issue list

Each issue should display:

- Original word, phrase, or sentence.
- Suggested correction.
- Short explanation.
- Interview date and context.
- Confidence or uncertainty indicator when available.
- Current review status.
- Practice action.

Allow users to mark an issue as confirmed, dismiss an incorrect suggestion, or add it to their practice queue.

### Issue detail page or drawer

Display the original evidence and proposed correction side by side.

For pronunciation issues, show a pronunciation guide, phonetic information when supplied by the backend, and available reference audio.

For grammar issues, show the original sentence, corrected sentence, and concise explanation.

For suspected transcription errors, clearly indicate that the system may have misunderstood the speaker rather than assuming the speaker made a mistake.

## 12. Pronunciation Practice

Create an interactive practice interface.

A typical practice flow:

1. Display the target word or sentence.
2. Play the available reference pronunciation.
3. Allow the user to listen again.
4. Record the user's attempt.
5. Upload the attempt to Django.
6. Display the backend's assessment.
7. Let the user repeat the exercise.
8. Save the attempt and progress.

Show:

- Target word or sentence.
- Reference audio controls.
- Microphone and recording timer.
- Attempt history.
- Recognized transcript.
- Assessment details.
- Practice again button.
- Mark as mastered action when appropriate.

Only display phoneme-level scores when the backend provides an appropriate assessment. Do not invent pronunciation scores from transcription similarity alone.

Keep the experience encouraging, specific, and non-judgmental.

## 13. Sentence and Grammar Practice

Create exercises that help the user speak clearer, more professional English.

Each exercise can contain:

- Original sentence.
- Suggested corrected sentence.
- Explanation of the grammar or vocabulary issue.
- Reference audio when available.
- Record and replay controls.
- Recognized attempt transcript.
- Feedback from the backend.
- Practice history.

Allow users to practise the corrected sentence and revisit previous mistakes.

Avoid overwhelming the user with too many corrections at once. Support practising one issue at a time.

## 14. Communication Progress Page

Build a progress dashboard that helps users understand improvement over time.

Include:

- Speaking-rate history.
- Filler-word frequency.
- Pause and fluency trends.
- Pronunciation practice completion.
- Grammar issues resolved.
- Mastered words and sentences.
- Frequently recurring issues.
- Practice streaks, if supported by actual history.
- Recent achievements based on real records.

Use Recharts with responsive, accessible charts.

Provide date filters and category filters where useful.

Do not treat a higher speaking rate as automatically better. Show target ranges only when supported by a suitable assessment rubric.

Do not compare accents or voice characteristics as indicators of personal worth or professionalism.

## 15. Interview History

Build a searchable, filterable interview history page.

Include:

- Interview title.
- Role.
- Interview type.
- Date.
- Duration.
- Completion status.
- Available report indicator.

Support:

- View transcript.
- View report.
- Review associated communication issues.
- Delete an interview when supported by the backend.

Ask for confirmation before destructive actions and accurately reflect backend success or failure.

## 16. Knowledge Sources

Create a knowledge-source management page for locally imported documentation.

Display:

- Source title.
- Source URL.
- License or permission metadata.
- Import status.
- Verification status.
- Import date.
- Available actions.

Allow users to search the knowledge base and inspect source details.

Only expose import actions that are supported by the backend. Explain that sources are used to ground technical interview questions and feedback.

Never display fabricated source citations.

## 17. Settings and Privacy

Create settings for:

- Preferred theme.
- Preferred interview interaction mode.
- Speech settings supported by the backend.
- Available local model status.
- Audio-retention preferences.
- Local data-management actions.
- Account settings.

Explain which records and audio files are retained.

Allow users to request deletion of their interviews, communication issues, and associated practice records when supported.

Do not transmit audio to external services. Use only the configured local backend.

Clearly distinguish frontend preferences from backend settings.

## 18. API Integration Layer

Implement a centralized, typed API client.

Create service modules for:

- Authentication.
- Interviews.
- Speech.
- Communication issues.
- Practice.
- Reports.
- Knowledge sources.

Use TypeScript interfaces for request and response structures.

Requirements:

- Centralize base URL configuration.
- Handle authentication and CSRF according to the backend setup.
- Handle timeouts and network errors.
- Parse backend errors safely.
- Support multipart audio uploads.
- Avoid duplicate API requests and accidental double submissions.
- Use loading, success, empty, and failure states.
- Do not hardcode production data into the UI.
- Use mock data only in clearly identified development fixtures.

Do not create fake success states when an API request fails.

## 19. Accessibility and User Experience

Implement:

- Keyboard navigation.
- Visible focus states.
- Semantic HTML.
- Accessible labels for microphone and audio controls.
- Screen-reader-friendly recording status.
- Sufficient text contrast.
- Responsive forms and tables.
- Clear validation messages.
- Reduced-motion support.
- Helpful empty states.

Make audio playback, recording, and interview controls usable without relying on color alone.

## 20. Performance and Maintainability

- Use Server Components by default where appropriate.
- Use Client Components only when browser interaction or state requires them.
- Keep components small and reusable.
- Separate API services, types, hooks, and UI components.
- Avoid putting all logic in a single page.
- Lazy-load heavier charts and optional modules where beneficial.
- Avoid unnecessary client-side dependencies.
- Do not load AI models into the browser; AI inference belongs in the local Django services.
- Avoid storing transcripts or audio in localStorage.
- Ensure the application remains usable on a modest computer.

## 21. Suggested Frontend Structure

frontend/
  app/
    (auth)/
      login/
      register/
    (dashboard)/
      dashboard/
      interviews/
      history/
      english-lab/
      pronunciation/
      communication-progress/
      knowledge/
      settings/
    interview/
      [id]/
    layout.tsx
    page.tsx
  components/
    layout/
    dashboard/
    interview/
    audio/
    communication/
    practice/
    charts/
    forms/
    ui/
  lib/
    api/
    auth/
    validation/
    utils/
  hooks/
  types/
  public/
  tests/
  .env.example
  README.md

Adapt the structure to the current project. Do not duplicate existing files or components.

## 22. Testing Requirements

Add tests for:

- Form validation.
- API client behavior.
- Authentication and protected routes.
- Loading, empty, and error states.
- Interview state transitions.
- Audio recording controls and permission failures.
- Preventing duplicate answer submissions.
- Learning-issue filters.
- Practice-attempt submission.
- Chart rendering with empty and populated data.
- Mobile navigation.
- Accessibility of critical controls.

Mock backend responses in frontend tests. Do not require real speech models or Ollama to run the normal frontend test suite.

## 23. Implementation Phases

Phase 1: Project setup, design system, responsive layout, authentication pages.

Phase 2: Dashboard, interview setup, and interview history.

Phase 3: Live interview UI, microphone recording, audio playback, and text fallback.

Phase 4: Interview reports and transcript review.

Phase 5: English Improvement Lab and issue-review workflows.

Phase 6: Pronunciation and grammar practice.

Phase 7: Communication progress charts and reports.

Phase 8: Knowledge-source management, settings, privacy, accessibility, and testing.

Implement each phase incrementally. Run linting, type checking, and tests before moving to the next phase.

## 24. Required Deliverables

Provide:

1. Complete working Next.js frontend source.
2. Responsive pages and reusable components.
3. Typed Django API integration.
4. Audio-recording and playback functionality.
5. Interview and English-practice workflows.
6. Environment-variable example.
7. Automated tests.
8. Setup and run instructions for Windows.
9. Documentation identifying backend endpoints that still need implementation.
10. A summary of completed, partially completed, and deferred functionality.

Start by inspecting the repository and creating an implementation plan. Then build the application incrementally, verifying each phase. Do not claim that a workflow works until it has been tested against the relevant backend endpoint.