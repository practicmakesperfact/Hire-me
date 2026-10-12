import logging
from typing import Optional, Dict, Any
from services.llm.ollama_client import get_ollama_client
from apps.interviews.models import InterviewSession, InterviewEvaluation

logger = logging.getLogger(__name__)


class InterviewEvaluator:
    """Evaluates interview performance using LLM."""
    
    def __init__(self):
        self.ollama = get_ollama_client()
    
    def evaluate_interview(self, session: InterviewSession) -> Optional[InterviewEvaluation]:
        """Generate evaluation for completed interview."""
        if not self.ollama.is_available():
            logger.warning("Ollama not available, skipping evaluation")
            return None
        
        # Build context from interview turns
        turns_context = self._build_turns_context(session)
        
        # Generate evaluation
        prompt = f"""Evaluate this technical interview performance.

Interview Topic: {session.topic.name if session.topic else 'General'}
Interview Type: {session.interview_type}
Difficulty: {session.difficulty}

Interview Conversation:
{turns_context}

Provide a structured evaluation with:
1. Technical accuracy score (0-10)
2. Completeness score (0-10)
3. Reasoning quality score (0-10)
4. Answer organization score (0-10)
5. Overall feedback (2-3 sentences)
6. Key strengths (bullet points)
7. Areas for improvement (bullet points)

Respond with JSON in this format:
{{
    "technical_score": 8.5,
    "completeness_score": 7.0,
    "reasoning_score": 8.0,
    "organization_score": 7.5,
    "overall_feedback": "Strong technical knowledge...",
    "strengths": "- Good understanding of concepts\\n- Clear explanations",
    "improvements": "- Could provide more examples\\n- Expand on edge cases"
}}"""
        
        system_prompt = """You are an experienced technical interviewer. 
Evaluate answers based on technical accuracy, completeness, reasoning, and organization.
Be fair but constructive. Focus on what the candidate demonstrated."""
        
        result = self.ollama.generate_structured(
            prompt=prompt,
            system=system_prompt,
            temperature=0.3  # Lower temperature for consistent evaluation
        )
        
        if not result:
            logger.error("Failed to generate evaluation")
            return None
        
        # Create evaluation record
        try:
            evaluation = InterviewEvaluation.objects.create(
                session=session,
                technical_score=result.get('technical_score'),
                completeness_score=result.get('completeness_score'),
                reasoning_score=result.get('reasoning_score'),
                organization_score=result.get('organization_score'),
                overall_feedback=result.get('overall_feedback', ''),
                strengths=result.get('strengths', ''),
                improvements=result.get('improvements', '')
            )
            return evaluation
        except Exception as e:
            logger.error(f"Failed to save evaluation: {e}")
            return None
    
    def _build_turns_context(self, session: InterviewSession) -> str:
        """Build formatted context from interview turns."""
        turns = session.turns.all().order_by('turn_number')
        
        context_parts = []
        for turn in turns:
            context_parts.append(f"Q{turn.turn_number}: {turn.question_text}")
            if turn.answer_text:
                context_parts.append(f"A{turn.turn_number}: {turn.answer_text}")
            else:
                context_parts.append(f"A{turn.turn_number}: [No answer provided]")
            context_parts.append("")  # Empty line between turns
        
        return "\n".join(context_parts)
    
    def evaluate_single_answer(
        self,
        question: str,
        answer: str,
        expected_answer: Optional[str] = None,
        key_points: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Evaluate a single question-answer pair."""
        if not self.ollama.is_available():
            return None
        
        prompt = f"""Evaluate this interview answer.

Question: {question}

Answer: {answer}"""
        
        if expected_answer:
            prompt += f"\n\nExpected Answer: {expected_answer}"
        
        if key_points:
            prompt += f"\n\nKey Points to Cover: {key_points}"
        
        prompt += """

Provide evaluation with:
- Accuracy score (0-10)
- Completeness score (0-10)
- Brief feedback (1-2 sentences)

Respond with JSON:
{
    "accuracy": 8.0,
    "completeness": 7.0,
    "feedback": "Good answer covering main points..."
}"""
        
        return self.ollama.generate_structured(
            prompt=prompt,
            temperature=0.3
        )
