"""
AI Self-Review Module

Implements comprehensive answer review and validation using multiple criteria.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
from mcp.types import McpError

class ReviewCriterion(Enum):
    """Review criteria categories"""
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    CLARITY = "clarity"
    CONSISTENCY = "consistency"

@dataclass
class ReviewFinding:
    """Individual review finding"""
    criterion: ReviewCriterion
    score: float
    details: str
    suggestions: List[str]

@dataclass
class ReviewResult:
    """Complete review result"""
    findings: List[ReviewFinding]
    overall_score: float
    needs_revision: bool
    revision_suggestions: List[str]

class AnswerReviewer:
    """
    Implements comprehensive answer review functionality.
    
    Features:
    - Multi-criteria evaluation
    - Consistency checking
    - Improvement suggestions
    - Source verification
    """
    
    def __init__(self):
        self.criteria_weights = {
            ReviewCriterion.COMPLETENESS: 0.25,
            ReviewCriterion.RELEVANCE: 0.25,
            ReviewCriterion.ACCURACY: 0.2,
            ReviewCriterion.CLARITY: 0.15,
            ReviewCriterion.CONSISTENCY: 0.15
        }
    
    async def review(
        self,
        question: str,
        answer: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReviewResult:
        """
        Perform comprehensive answer review.
        
        Args:
            question: Original question
            answer: Answer to review
            context: Optional additional context
            
        Returns:
            ReviewResult with findings and suggestions
            
        Raises:
            McpError: If review fails
        """
        try:
            findings = []
            
            # Check completeness
            findings.append(await self._check_completeness(question, answer))
            
            # Check relevance
            findings.append(await self._check_relevance(question, answer))
            
            # Check accuracy
            findings.append(await self._check_accuracy(question, answer))
            
            # Check clarity
            findings.append(self._check_clarity(answer))
            
            # Check consistency
            findings.append(self._check_consistency(answer, context))
            
            # Calculate overall score
            overall_score = sum(
                finding.score * self.criteria_weights[finding.criterion]
                for finding in findings
            )
            
            # Determine if revision needed
            needs_revision = overall_score < 0.7 or any(
                finding.score < 0.5 for finding in findings
            )
            
            # Compile revision suggestions
            revision_suggestions = []
            for finding in findings:
                if finding.score < 0.8:
                    revision_suggestions.extend(finding.suggestions)
            
            return ReviewResult(
                findings=findings,
                overall_score=overall_score,
                needs_revision=needs_revision,
                revision_suggestions=revision_suggestions
            )
            
        except Exception as e:
            raise McpError(f"Answer review failed: {str(e)}")

    async def _check_completeness(
        self,
        question: str,
        answer: str
    ) -> ReviewFinding:
        """Check if answer fully addresses the question"""
        # Extract question components
        components = self._extract_question_components(question)
        
        # Check which components are addressed
        addressed = set()
        for component in components:
            if component.lower() in answer.lower():
                addressed.add(component)
        
        # Calculate completeness score
        score = len(addressed) / len(components) if components else 0.5
        
        # Generate suggestions
        suggestions = []
        missing = components - addressed
        if missing:
            suggestions.append(
                f"Address these aspects: {', '.join(missing)}"
            )
        
        return ReviewFinding(
            criterion=ReviewCriterion.COMPLETENESS,
            score=score,
            details=f"Addressed {len(addressed)}/{len(components)} components",
            suggestions=suggestions
        )

    async def _check_relevance(
        self,
        question: str,
        answer: str
    ) -> ReviewFinding:
        """Check answer relevance to question"""
        # Use enhanced search to verify relevance
        from ..research.enhanced_search import EnhancedSearchManager
        
        search_manager = EnhancedSearchManager()
        search_results = await search_manager.search(question, min_results=2)
        
        # Compare answer with search results
        relevance_scores = []
        for result in search_results:
            score = self._calculate_text_similarity(
                answer,
                result.content
            )
            relevance_scores.append(score)
        
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        suggestions = []
        if avg_relevance < 0.6:
            suggestions.append("Answer may need more specific details from reliable sources")
        
        return ReviewFinding(
            criterion=ReviewCriterion.RELEVANCE,
            score=avg_relevance,
            details=f"Average relevance score: {avg_relevance:.2f}",
            suggestions=suggestions
        )

    async def _check_accuracy(
        self,
        question: str,
        answer: str
    ) -> ReviewFinding:
        """Verify answer accuracy"""
        # Use search to verify facts
        from ..research.enhanced_search import EnhancedSearchManager
        
        search_manager = EnhancedSearchManager()
        verification_results = await search_manager.search(
            f"verify {answer}",
            min_results=2
        )
        
        # Check for contradictions
        contradictions = []
        support = []
        
        for result in verification_results:
            if self._contradicts(answer, result.content):
                contradictions.append(result.content)
            else:
                support.append(result.content)
        
        # Calculate accuracy score
        score = len(support) / (len(support) + len(contradictions))
        
        suggestions = []
        if contradictions:
            suggestions.append("Found potential contradictions with reliable sources")
        
        return ReviewFinding(
            criterion=ReviewCriterion.ACCURACY,
            score=score,
            details=f"Found {len(support)} supporting and {len(contradictions)} contradicting sources",
            suggestions=suggestions
        )

    def _check_clarity(self, answer: str) -> ReviewFinding:
        """Check answer clarity and readability"""
        # Check sentence structure
        sentences = answer.split('.')
        avg_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        # Check for complex words
        complex_words = set()
        for word in answer.split():
            if len(word) > 12:  # Arbitrary threshold
                complex_words.add(word)
        
        # Calculate clarity score
        length_score = 1.0 if 10 <= avg_length <= 20 else 0.5
        complexity_score = 1.0 - (len(complex_words) / len(answer.split()) * 2)
        score = (length_score + complexity_score) / 2
        
        suggestions = []
        if avg_length > 20:
            suggestions.append("Consider breaking down long sentences")
        if complex_words:
            suggestions.append(f"Consider simplifying terms: {', '.join(complex_words)}")
        
        return ReviewFinding(
            criterion=ReviewCriterion.CLARITY,
            score=score,
            details=f"Average sentence length: {avg_length:.1f} words",
            suggestions=suggestions
        )

    def _check_consistency(
        self,
        answer: str,
        context: Optional[Dict[str, Any]]
    ) -> ReviewFinding:
        """Check internal consistency"""
        # Look for contradictory statements
        contradictions = self._find_contradictions(answer)
        
        # Check consistency with context
        context_conflicts = []
        if context and "previous_answers" in context:
            for prev_answer in context["previous_answers"]:
                if self._contradicts(answer, prev_answer):
                    context_conflicts.append(prev_answer)
        
        # Calculate consistency score
        score = 1.0
        if contradictions:
            score *= 0.5
        if context_conflicts:
            score *= 0.7
        
        suggestions = []
        if contradictions:
            suggestions.append("Found potential internal contradictions")
        if context_conflicts:
            suggestions.append("Answer may conflict with previous responses")
        
        return ReviewFinding(
            criterion=ReviewCriterion.CONSISTENCY,
            score=score,
            details="Checked for internal and contextual consistency",
            suggestions=suggestions
        )

    def _extract_question_components(self, question: str) -> Set[str]:
        """Extract key components that need to be addressed"""
        # Remove question words
        question = question.lower()
        for word in ["what", "why", "how", "when", "where", "who"]:
            question = question.replace(word, "")
            
        # Split on conjunctions
        parts = question.replace(" and ", ", ").replace(" or ", ", ").split(",")
        
        # Clean and return unique components
        return {part.strip() for part in parts if len(part.strip()) > 0}

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Convert to word sets
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0

    def _contradicts(self, text1: str, text2: str) -> bool:
        """Check if texts contradict each other"""
        # Look for opposing statements
        negation_markers = {"not", "never", "no", "isn't", "aren't", "wasn't", "weren't"}
        
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Check if one text contains negation of a statement in the other
        for sentence in text1_lower.split('.'):
            sentence = sentence.strip()
            if any(marker in sentence for marker in negation_markers):
                # Remove negation and check if positive form exists in text2
                positive = sentence
                for marker in negation_markers:
                    positive = positive.replace(marker, "")
                if positive.strip() in text2_lower:
                    return True
        
        return False

    def _find_contradictions(self, text: str) -> List[str]:
        """Find contradictory statements within text"""
        contradictions = []
        sentences = text.split('.')
        
        for i, sentence1 in enumerate(sentences):
            for sentence2 in sentences[i+1:]:
                if self._contradicts(sentence1, sentence2):
                    contradictions.append(f"{sentence1} vs {sentence2}")
        
        return contradictions
