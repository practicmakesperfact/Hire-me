import logging
from typing import Optional, Dict, Any, List
from django.db import transaction
from apps.interviews.models import InterviewSession, InterviewTurn
from apps.questions.models import Question
from services.llm.ollama_client import get_ollama_client
from services.evaluation.interview_evaluator import InterviewEvaluator
from services.communication_analyzer.issue_detector import IssueDetector

logger = logging.getLogger(__name__)


class InterviewOrchestrator:
    """Orchestrates interview flow with LLM integration."""
    
    def __init__(self):
        self.ollama = get_ollama_client()
        self.evaluator = InterviewEvaluator()
        self.issue_detector = IssueDetector()
    
    def generate_next_question(
        self,
        session: InterviewSession,
        use_llm: bool = True
    ) -> Optional[str]:
        """Generate or select next interview question."""
        
        # If LLM available and requested, generate dynamic question
        if use_llm and self.ollama.is_available():
            return self._generate_question_with_llm(session)
        
        # Otherwise, select from question bank
        return self._select_question_from_bank(session)
    
    def _generate_question_with_llm(self, session: InterviewSession) -> Optional[str]:
        """Generate question using LLM based on context."""
        
        # Build context from previous turns
        previous_turns = session.turns.all().order_by('turn_number')
        context = self._build_conversation_context(previous_turns)
        
        prompt = f"""You are conducting a technical interview.

Interview Details:
- Role: {session.role.name if session.role else 'General'}
- Topic: {session.topic.name if session.topic else 'General'}
- Difficulty: {session.difficulty}
- Type: {session.interview_type}

{context}

Generate the next interview question. The question should:
1. Be relevant to the topic and role
2. Match the difficulty level
3. Build upon previous answers if applicable
4. Be clear and specific

Respond with ONLY the question text, no additional formatting."""
        
        system_prompt = f"""You are an experienced {session.interview_type} interviewer.
Ask clear, relevant questions appropriate for a {session.difficulty} level candidate.
Never interrupt or correct the candidate during the interview."""
        
        question = self.ollama.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.8  # Higher creativity for question generation
        )
        
        return question
    
    def _select_question_from_bank(self, session: InterviewSession) -> Optional[str]:
        """Select appropriate question from question bank."""
        
        # Get questions matching topic and difficulty
        questions = Question.objects.filter(
            topic=session.topic,
            difficulty=session.difficulty,
            question_type=session.interview_type
        )
        
        # Exclude already asked questions
        asked_questions = session.turns.values_list('question_text', flat=True)
        questions = questions.exclude(question_text__in=asked_questions)
        
        # Get random question
        question = questions.order_by('?').first()
        
        if question:
            return question.question_text
        
        # Fallback to any question in topic
        question = Question.objects.filter(topic=session.topic).order_by('?').first()
        return question.question_text if question else None
    
    def _build_conversation_context(self, turns) -> str:
        """Build conversation context from previous turns."""
        if not turns:
            return "This is the first question."
        
        context_parts = ["Previous conversation:"]
        for turn in turns[:5]:  # Last 5 turns for context
            context_parts.append(f"Q: {turn.question_text}")
            if turn.answer_text:
                context_parts.append(f"A: {turn.answer_text[:200]}...")  # Truncate long answers
        
        return "\n".join(context_parts)
    
    def generate_followup_question(
        self,
        session: InterviewSession,
        last_turn: InterviewTurn
    ) -> Optional[str]:
        """Generate follow-up question based on last answer."""
        
        if not self.ollama.is_available():
            return self._select_question_from_bank(session)
        
        prompt = f"""Based on the candidate's previous answer, generate a relevant follow-up question.

Original Question: {last_turn.question_text}

Candidate's Answer: {last_turn.answer_text}

Topic: {session.topic.name if session.topic else 'General'}
Difficulty: {session.difficulty}

Generate a follow-up question that:
1. Digs deeper into their understanding
2. Explores related concepts
3. Tests practical application
4. Is appropriate for {session.difficulty} level

Respond with ONLY the question text."""
        
        system_prompt = "You are an experienced technical interviewer asking insightful follow-up questions."
        
        question = self.ollama.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.8
        )
        
        return question
    
    @transaction.atomic
    def process_answer_and_generate_next(
        self,
        session: InterviewSession,
        answer_text: str,
        current_question: str,
        analyze_communication: bool = True
    ) -> Dict[str, Any]:
        """Process answer and generate next question."""
        
        # Save current turn
        turn_number = session.turns.count() + 1
        turn = InterviewTurn.objects.create(
            session=session,
            turn_number=turn_number,
            question_text=current_question,
            answer_text=answer_text
        )
        
        # Silently detect communication issues (doesn't interrupt)
        issues_detected = 0
        if analyze_communication:
            issues = self.issue_detector.analyze_turn_silent(turn)
            for issue in issues:
                issue.save()
            issues_detected = len(issues)
            logger.info(f"Detected {issues_detected} communication issues (saved silently)")
        
        # Generate next question
        next_question = self.generate_next_question(session)
        
        return {
            'turn_number': turn_number,
            'next_question': next_question,
            'can_continue': next_question is not None,
            'issues_detected': issues_detected  # For logging only, not shown to user
        }
    
    def finish_interview_and_evaluate(
        self,
        session: InterviewSession,
        generate_evaluation: bool = True
    ) -> Optional[Dict[str, Any]]:
        """Finish interview and optionally generate evaluation."""
        
        session.status = 'finished'
        session.save()
        
        if not generate_evaluation:
            return None
        
        # Generate evaluation using LLM
        evaluation = self.evaluator.evaluate_interview(session)
        
        if evaluation:
            return {
                'technical_score': evaluation.technical_score,
                'completeness_score': evaluation.completeness_score,
                'reasoning_score': evaluation.reasoning_score,
                'organization_score': evaluation.organization_score,
                'overall_feedback': evaluation.overall_feedback,
                'strengths': evaluation.strengths,
                'improvements': evaluation.improvements
            }
        
        return None
