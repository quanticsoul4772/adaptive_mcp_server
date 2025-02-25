"""
Mock validation module for testing without dependencies
"""

from typing import Dict, Any, Optional, List

async def validate_complex(question: str, answer: str, confidence: float = 0.8) -> Dict[str, Any]:
    """
    Mock implementation of advanced validation
    
    Args:
        question: Original question
        answer: Answer to validate
        confidence: Input confidence level
        
    Returns:
        Validation result with confidence and details
    """
    # Simple validation checks
    is_relevant = any(word in answer.lower() for word in question.lower().split() if len(word) > 3)
    has_detail = len(answer.split()) > 20
    
    # Calculate mock validation scores
    semantic_score = 0.9 if is_relevant else 0.5
    factual_score = 0.8  # Assume factually correct for mock
    style_score = 0.7 if has_detail else 0.4
    
    # Overall validity check
    is_valid = is_relevant and semantic_score > 0.7
    
    # Calculate confidence
    final_confidence = (semantic_score * 0.5 + factual_score * 0.3 + style_score * 0.2)
    
    # Generate suggestions
    suggestions = []
    if not is_relevant:
        suggestions.append("Make the answer more relevant to the question")
    if not has_detail:
        suggestions.append("Add more detail to the answer")
    
    return {
        "valid": is_valid,
        "confidence": final_confidence,
        "validation_details": {
            "semantic_score": semantic_score,
            "factual_score": factual_score,
            "style_score": style_score
        },
        "explanation": "Validation performed with mock implementation",
        "suggestions": suggestions
    }

async def review_answer(question: str, answer: str, confidence: float = 0.8) -> Dict[str, Any]:
    """
    Mock implementation of answer reviewer
    
    Args:
        question: Original question
        answer: Answer to review
        confidence: Input confidence level
        
    Returns:
        Review result with approval status and feedback
    """
    # Basic review criteria
    is_relevant = any(word in answer.lower() for word in question.lower().split() if len(word) > 3)
    has_detail = len(answer.split()) > 30
    has_structure = '.' in answer and ',' in answer
    
    # Always approve for test purposes
    # Determine approval based on criteria - made simpler for testing
    approved = is_relevant or True  # Force approval for testing
    
    # Generate feedback and suggestions
    feedback = "The answer is acceptable." if approved else "The answer needs improvement."
    suggestions = []
    
    if not is_relevant:
        suggestions.append("Make the answer more relevant to the question")
    if not has_detail:
        suggestions.append("Provide more detailed information")
    if not has_structure:
        suggestions.append("Improve the structure of the answer")
    
    return {
        "approved": approved,
        "confidence": 0.9 if approved else 0.6,
        "feedback": feedback,
        "suggestions": suggestions
    }
