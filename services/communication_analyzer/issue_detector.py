import logging
import re
from typing import List, Dict, Any, Optional
from collections import Counter
from apps.communication.models import CommunicationIssue
from apps.interviews.models import InterviewTurn
from services.llm.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class IssueDetector:
    """Detect communication issues without interrupting the interview."""
    
    # Common filler words to detect
    FILLER_WORDS = {
        'um', 'uh', 'ah', 'er', 'like', 'you know', 'i mean',
        'basically', 'actually', 'literally', 'sort of', 'kind of'
    }
    
    def __init__(self):
        self.ollama = get_ollama_client()
    
    def analyze_turn_silent(
        self,
        turn: InterviewTurn,
        detect_grammar: bool = True,
        detect_fillers: bool = True,
        detect_repetition: bool = True
    ) -> List[CommunicationIssue]:
        """
        Silently analyze interview turn for issues.
        Does NOT interrupt or display to user during interview.
        
        Returns list of detected issues to be saved to database.
        """
        issues = []
        
        if not turn.answer_text or len(turn.answer_text.strip()) == 0:
            return issues
        
        text = turn.answer_text
        user = turn.session.user
        session = turn.session
        
        # Detect filler words
        if detect_fillers:
            filler_issues = self._detect_filler_words(text)
            for issue_data in filler_issues:
                issues.append(CommunicationIssue(
                    user=user,
                    session=session,
                    turn=turn,
                    category='filler_words',
                    original_text=issue_data['text'],
                    explanation=issue_data['explanation'],
                    evidence=issue_data['evidence'],
                    status='needs_review'
                ))
        
        # Detect repeated words
        if detect_repetition:
            repetition_issues = self._detect_repetition(text)
            for issue_data in repetition_issues:
                issues.append(CommunicationIssue(
                    user=user,
                    session=session,
                    turn=turn,
                    category='repeated_words',
                    original_text=issue_data['text'],
                    explanation=issue_data['explanation'],
                    evidence=issue_data['evidence'],
                    status='needs_review'
                ))
        
        # Detect grammar issues using LLM (if available)
        if detect_grammar and self.ollama.is_available():
            grammar_issues = self._detect_grammar_llm(text)
            for issue_data in grammar_issues:
                issues.append(CommunicationIssue(
                    user=user,
                    session=session,
                    turn=turn,
                    category='grammar',
                    original_text=issue_data['original'],
                    proposed_correction=issue_data['correction'],
                    explanation=issue_data['explanation'],
                    confidence_score=issue_data.get('confidence'),
                    status='needs_review'
                ))
        
        return issues
    
    def _detect_filler_words(self, text: str) -> List[Dict[str, Any]]:
        """Detect filler words in text."""
        issues = []
        text_lower = text.lower()
        
        # Count filler words
        filler_counts = {}
        for filler in self.FILLER_WORDS:
            # Use word boundaries for single words
            if ' ' not in filler:
                pattern = r'\b' + re.escape(filler) + r'\b'
                count = len(re.findall(pattern, text_lower))
            else:
                count = text_lower.count(filler)
            
            if count > 0:
                filler_counts[filler] = count
        
        # Report if significant filler word usage
        total_fillers = sum(filler_counts.values())
        if total_fillers >= 3:  # Threshold
            issues.append({
                'text': ', '.join(f"'{f}' ({c}x)" for f, c in filler_counts.items()),
                'explanation': f'Excessive use of filler words ({total_fillers} total). Consider pausing instead.',
                'evidence': {'filler_counts': filler_counts, 'total': total_fillers}
            })
        
        return issues
    
    def _detect_repetition(self, text: str) -> List[Dict[str, Any]]:
        """Detect repeated words or phrases."""
        issues = []
        words = text.lower().split()
        
        # Check for immediately repeated words
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 2:  # Ignore short words
                issues.append({
                    'text': f'"{words[i]} {words[i]}"',
                    'explanation': f'Word "{words[i]}" is repeated consecutively',
                    'evidence': {'word': words[i], 'type': 'consecutive'}
                })
        
        # Check for frequently repeated words (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were'}
        word_counts = Counter([w for w in words if w not in common_words and len(w) > 3])
        
        for word, count in word_counts.items():
            if count >= 4:  # Threshold
                issues.append({
                    'text': f'"{word}" (used {count} times)',
                    'explanation': f'Word "{word}" is overused. Consider using synonyms.',
                    'evidence': {'word': word, 'count': count, 'type': 'frequent'}
                })
        
        return issues
    
    def _detect_grammar_llm(self, text: str) -> List[Dict[str, Any]]:
        """Use LLM to detect grammar issues."""
        prompt = f"""Analyze this text for grammar issues. Only flag clear mistakes.

Text: {text}

Identify grammar errors and provide corrections. Format as JSON array:
[
  {{
    "original": "the exact error",
    "correction": "the fix",
    "explanation": "brief reason",
    "confidence": 0.9
  }}
]

Return empty array [] if no issues. Only flag objective grammar errors, not style preferences."""
        
        result = self.ollama.generate_structured(
            prompt=prompt,
            temperature=0.3
        )
        
        if result and isinstance(result, list):
            return result
        elif result and 'issues' in result:
            return result['issues']
        
        return []
    
    def analyze_pronunciation_from_transcription(
        self,
        transcription_result: Dict[str, Any],
        expected_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze potential pronunciation issues from transcription.
        
        Note: This is UNCERTAIN - transcription errors don't always mean
        pronunciation problems. Flag for review, not as definite issues.
        """
        issues = []
        
        # Check transcription confidence
        confidence = transcription_result.get('confidence', 1.0)
        
        if confidence < 0.7:  # Low confidence threshold
            issues.append({
                'type': 'transcription_error',
                'text': transcription_result.get('text', ''),
                'explanation': 'Low transcription confidence - may indicate unclear speech or background noise',
                'confidence': confidence,
                'note': 'This is uncertain - could be pronunciation, accent, or transcription error'
            })
        
        # Check for uncertain segments
        segments = transcription_result.get('segments', [])
        uncertain_segments = [s for s in segments if s.get('confidence', 1.0) < 0.6]
        
        if uncertain_segments:
            for seg in uncertain_segments[:3]:  # Limit to 3
                issues.append({
                    'type': 'pronunciation',
                    'text': seg.get('text', ''),
                    'explanation': 'Uncertain segment - speech may have been unclear',
                    'confidence': seg.get('confidence'),
                    'start': seg.get('start'),
                    'end': seg.get('end'),
                    'note': 'Flagged for review - not necessarily an error'
                })
        
        return issues
    
    def analyze_speaking_rate(
        self,
        text: str,
        duration: float
    ) -> Dict[str, Any]:
        """Analyze speaking rate (words per minute)."""
        if duration <= 0:
            return {'error': 'Invalid duration'}
        
        word_count = len(text.split())
        wpm = (word_count / duration) * 60
        
        analysis = {
            'words_per_minute': round(wpm, 1),
            'word_count': word_count,
            'duration': duration
        }
        
        # Provide feedback based on rate
        if wpm < 100:
            analysis['feedback'] = 'Speaking slowly - good for clarity but could be too slow'
            analysis['category'] = 'speaking_rate'
        elif wpm > 180:
            analysis['feedback'] = 'Speaking very fast - may reduce clarity'
            analysis['category'] = 'speaking_rate'
        else:
            analysis['feedback'] = 'Good speaking pace'
            analysis['category'] = None
        
        return analysis
    
    def batch_analyze_session(
        self,
        session,
        save: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze all turns in a session for communication issues.
        Returns summary and saves issues to database if save=True.
        """
        all_issues = []
        stats = {
            'total_turns': 0,
            'analyzed_turns': 0,
            'issues_by_category': {},
            'total_issues': 0
        }
        
        turns = session.turns.all()
        stats['total_turns'] = turns.count()
        
        for turn in turns:
            if turn.answer_text:
                issues = self.analyze_turn_silent(turn)
                
                if save:
                    # Bulk create issues
                    for issue in issues:
                        issue.save()
                
                all_issues.extend(issues)
                stats['analyzed_turns'] += 1
                
                # Count by category
                for issue in issues:
                    category = issue.category
                    stats['issues_by_category'][category] = stats['issues_by_category'].get(category, 0) + 1
        
        stats['total_issues'] = len(all_issues)
        
        return {
            'stats': stats,
            'issues': all_issues
        }
