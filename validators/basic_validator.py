"""
Basic Answer Validator Module

Implements validation logic for answers produced by the reasoning modules.
Checks for relevance, completeness, and confidence based on multiple criteria.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re

@dataclass
class ValidationCriterion:
    """Single validation criterion with its weight and check function"""
    name: str
    weight: float
    check: callable
    description: str

@dataclass
class ValidationResult:
    """Complete validation result with detailed scoring"""
    valid: bool
    confidence: float
    criteria_scores: Dict[str, float]
    explanation: str
    suggestions: List[str]

class AnswerValidator:
    """
    Validates answers using multiple weighted criteria.
    
    Validation includes:
    - Question-answer relevance
    - Answer completeness
    - Source validation
    - Uncertainty checking
    """
    
    def __init__(self):
        self.criteria = [
            ValidationCriterion(
                name="relevance",
                weight=0.4,
                check=self._check_relevance,
                description="Checks if answer addresses the question"
            ),
            ValidationCriterion(
                name="completeness",
                weight=0.3,
                check=self._check_completeness,
                description="Checks if answer is complete"
            ),
            ValidationCriterion(
                name="uncertainty",
                weight=0.2,
                check=self._check_uncertainty,
                description="Checks for appropriate uncertainty indicators"
            ),
            ValidationCriterion(
                name="sources",
                weight=0.1,
                check=self._check_sources,
                description="Checks if answer references valid sources"
            )
        ]

    def validate(self, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate an answer against its question.
        
        Args:
            question: Original question
            answer: Proposed answer
            metadata: Optional metadata about the answer
            
        Returns:
            ValidationResult with detailed scoring and feedback
        """
        if not answer or not question:
            return ValidationResult(
                valid=False,
                confidence=0.0,
                criteria_scores={"input_validation": 0.0},
                explanation="Empty question or answer",
                suggestions=["Provide non-empty question and answer"]
            )

        # Calculate individual criteria scores
        scores = {}
        suggestions = []
        for criterion in self.criteria:
            score, feedback = criterion.check(question, answer, metadata)
            scores[criterion.name] = score
            if feedback:
                suggestions.append(feedback)

        # Calculate weighted confidence
        confidence = sum(
            criterion.weight * scores[criterion.name]
            for criterion in self.criteria
        )

        # Generate explanation
        strong_points = [
            name for name, score in scores.items()
            if score >= 0.8
        ]
        weak_points = [
            name for name, score in scores.items()
            if score < 0.6
        ]

        explanation = (
            f"Confidence score: {confidence:.2f}. "
            f"Strong aspects: {', '.join(strong_points) if strong_points else 'none'}. "
            f"Areas for improvement: {', '.join(weak_points) if weak_points else 'none'}."
        )

        return ValidationResult(
            valid=confidence >= 0.6,
            confidence=confidence,
            criteria_scores=scores,
            explanation=explanation,
            suggestions=suggestions
        )

    def _check_relevance(self, question: str, answer: str, metadata: Optional[Dict[str, Any]]) -> tuple[float, Optional[str]]:
        """Check if answer is relevant to question"""
        # Convert to sets of terms for comparison
        question_terms = set(re.findall(r'\w+', question.lower()))
        answer_terms = set(re.findall(r'\w+', answer.lower()))
        
        # Calculate overlap
        overlap = len(question_terms.intersection(answer_terms))
        score = min(1.0, overlap / len(question_terms) if question_terms else 0)
        
        feedback = None
        if score < 0.6:
            feedback = "Answer could better address key terms from the question"
            
        return score, feedback

    def _check_completeness(self, question: str, answer: str, metadata: Optional[Dict[str, Any]]) -> tuple[float, Optional[str]]:
        """Check if answer seems complete"""
        # Basic completeness checks
        has_sentence_end = bool(re.search(r'[.!?]$', answer.strip()))
        min_length = len(answer.split()) >= 5
        has_structure = ',' in answer or ';' in answer or len(answer.split('.')) > 1
        
        score = sum([
            0.4 if has_sentence_end else 0,
            0.3 if min_length else 0,
            0.3 if has_structure else 0
        ])
        
        feedback = None
        if not has_sentence_end:
            feedback = "Answer should be a complete sentence"
        elif not min_length:
            feedback = "Answer seems too brief"
            
        return score, feedback

    def _check_uncertainty(self, question: str, answer: str, metadata: Optional[Dict[str, Any]]) -> tuple[float, Optional[str]]:
        """Check if answer appropriately expresses uncertainty"""
        # Define uncertainty indicators
        certainty_phrases = {'definitely', 'certainly', 'always', 'never', 'absolutely'}
        uncertainty_phrases = {'likely', 'probably', 'may', 'might', 'could', 'appears', 'seems'}
        
        answer_lower = answer.lower()
        has_certainty = any(phrase in answer_lower for phrase in certainty_phrases)
        has_uncertainty = any(phrase in answer_lower for phrase in uncertainty_phrases)
        
        # Check if uncertainty is warranted based on metadata confidence
        metadata_confidence = metadata.get('confidence', 0.8) if metadata else 0.8
        
        if metadata_confidence < 0.7 and not has_uncertainty:
            return 0.5, "Consider expressing more uncertainty given confidence level"
        elif metadata_confidence > 0.9 and has_uncertainty:
            return 0.7, "Could be more definitive given high confidence"
        
        return 1.0, None

    def _check_sources(self, question: str, answer: str, metadata: Optional[Dict[str, Any]]) -> tuple[float, Optional[str]]:
        """Check if answer cites sources when appropriate"""
        needs_citation = any(term in question.lower() for term in [
            'what is', 'who is', 'when did', 'where is', 'why does'
        ])
        
        has_source = (
            'source:' in answer.lower() or
            'according to' in answer.lower() or
            bool(re.search(r'\(\d{4}\)', answer)) or  # Year citation
            bool(metadata and metadata.get('sources'))
        )
        
        if needs_citation and not has_source:
            return 0.5, "Consider citing sources for factual claims"
        
        return 1.0, None

def validate_answer(question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    High-level validation function that returns results in standard format.
    
    Args:
        question: Original question
        answer: Proposed answer
        metadata: Optional metadata about the answer generation
        
    Returns:
        Dict containing validation results
    """
    validator = AnswerValidator()
    result = validator.validate(question, answer, metadata)
    
    return {
        "valid": result.valid,
        "confidence": result.confidence,
        "explanation": result.explanation,
        "criteria_scores": result.criteria_scores,
        "suggestions": result.suggestions
    }
