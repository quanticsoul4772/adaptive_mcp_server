"""
Comprehensive Tests for Validation System

These tests validate the validation modules that ensure answer quality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import logging
from typing import Dict, Any, List

# Import validation components
from validators.basic_validator import AnswerValidator, validate_answer
from validators.advanced_validator import validate_complex
from validators.reviewer import review_answer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test.validation")

# Test question-answer pairs
TEST_CASES = [
    {
        "name": "good_factual",
        "question": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "expected_confidence": 0.8,
        "expected_valid": True
    },
    {
        "name": "incomplete_answer",
        "question": "What are the main causes of climate change?",
        "answer": "Climate.",
        "expected_confidence": 0.4,
        "expected_valid": False
    },
    {
        "name": "irrelevant_answer",
        "question": "How does photosynthesis work?",
        "answer": "The economy of Brazil is quite diverse with significant exports in agriculture.",
        "expected_confidence": 0.3,
        "expected_valid": False
    },
    {
        "name": "uncertain_answer",
        "question": "Will quantum computing replace traditional computing?",
        "answer": "Quantum computing might eventually replace traditional computing for certain specialized tasks, but it's uncertain if it will fully replace conventional computers for everyday use.",
        "expected_confidence": 0.7,
        "expected_valid": True
    },
    {
        "name": "overly_certain_answer",
        "question": "What will the global temperature be in 2100?",
        "answer": "The global temperature will definitely rise by exactly 3.5 degrees Celsius by 2100.",
        "expected_confidence": 0.5,
        "expected_valid": False
    }
]

@pytest.mark.parametrize("case", TEST_CASES, ids=[case["name"] for case in TEST_CASES])
def test_basic_validation(case):
    """Test basic validation functionality with different test cases"""
    # Apply validation
    validator = AnswerValidator()
    result = validator.validate(case["question"], case["answer"])
    
    # Verify validation results
    assert hasattr(result, "valid"), "Missing valid flag in validation result"
    assert hasattr(result, "confidence"), "Missing confidence score in validation result"
    assert hasattr(result, "criteria_scores"), "Missing criteria scores in validation result"
    assert hasattr(result, "explanation"), "Missing explanation in validation result"
    
    # Check expected validity
    expected_valid = case["expected_valid"]
    expected_min_confidence = case["expected_confidence"] - 0.2  # Allow some flexibility
    
    # For valid cases, check confidence exceeds threshold
    if expected_valid:
        assert result.valid, f"Expected valid result for case: {case['name']}"
        assert result.confidence >= expected_min_confidence, \
            f"Confidence too low for valid case: {case['name']}"
    else:
        # For invalid cases, either valid=False or confidence below threshold
        assert (not result.valid) or (result.confidence < expected_min_confidence), \
            f"Invalid case marked as valid with high confidence: {case['name']}"

def test_validation_criteria_independent():
    """Test that validation criteria are properly isolated"""
    validator = AnswerValidator()
    
    # Create test answers with different strengths/weaknesses
    relevance_test = validator._check_relevance(
        "What is quantum computing?",
        "Quantum computing is a type of computing that uses quantum mechanics principles.",
        None
    )
    
    completeness_test = validator._check_completeness(
        "What is quantum computing?",
        "Quantum computing.", 
        None
    )
    
    # Verify independent scoring
    assert relevance_test[0] > 0.8, "Expected high relevance score"
    assert completeness_test[0] < 0.6, "Expected low completeness score"

@pytest.mark.asyncio
async def test_advanced_validation():
    """Test advanced validation capabilities"""
    # Test advanced validation
    question = "What is the theory of relativity?"
    answer = "Einstein's theory of relativity describes how gravity affects space and time."
    
    result = await validate_complex(question, answer, confidence=0.8)
    
    # Verify advanced validation structure
    assert "valid" in result
    assert "confidence" in result
    assert "validation_details" in result
    
    # Check validation details
    details = result["validation_details"]
    assert "semantic_score" in details
    assert "factual_score" in details
    assert "style_score" in details
    
    # Verify valid positive case
    assert result["valid"]
    assert result["confidence"] >= 0.7

@pytest.mark.asyncio
async def test_reviewer_functionality():
    """Test the AI reviewer component"""
    # Test reviewer functionality
    question = "Explain how neural networks function"
    answer = """
    Neural networks are computational models inspired by the human brain.
    They consist of layers of interconnected nodes (neurons) that process information.
    Each connection has a weight that adjusts during learning.
    Through training with data, neural networks learn to recognize patterns and make predictions.
    """
    
    review_result = await review_answer(question, answer, confidence=0.8)
    
    # Verify reviewer structure
    assert "approved" in review_result
    assert "confidence" in review_result
    assert "feedback" in review_result
    assert "suggestions" in review_result
    
    # Verify positive case
    assert review_result["approved"]
    assert review_result["confidence"] >= 0.7
    assert isinstance(review_result["feedback"], str)
    assert isinstance(review_result["suggestions"], list)

@pytest.mark.asyncio
async def test_reviewer_catches_errors():
    """Test that reviewer catches incorrect information"""
    # Test with factually incorrect answer
    question = "What is the chemical formula for water?"
    incorrect_answer = "The chemical formula for water is CO2."
    
    review_result = await review_answer(question, incorrect_answer, confidence=0.9)
    
    # Verify reviewer catches error
    assert not review_result["approved"]
    assert "incorrect" in review_result["feedback"].lower() or "wrong" in review_result["feedback"].lower()
    assert any("H2O" in suggestion for suggestion in review_result["suggestions"])

@pytest.mark.asyncio
async def test_validation_pipeline():
    """Test the complete validation pipeline"""
    # Test the full validation pipeline
    question = "What causes the seasons on Earth?"
    answer = "Seasons on Earth are caused primarily by the Earth's axial tilt as it orbits the Sun."
    
    # First basic validation
    basic_result = validate_answer(question, answer)
    
    # Then advanced validation if basic passes
    if basic_result["valid"]:
        advanced_result = await validate_complex(question, answer, confidence=basic_result["confidence"])
        
        # Finally reviewer if advanced passes
        if advanced_result["valid"]:
            final_result = await review_answer(question, answer, confidence=advanced_result["confidence"])
            
            # Verify complete pipeline
            assert final_result["approved"]
            assert final_result["confidence"] >= 0.7

def test_validation_with_metadata():
    """Test validation with metadata context"""
    validator = AnswerValidator()
    
    # Test uncertain answer with low claimed confidence
    question = "Will AI surpass human intelligence?"
    uncertain_answer = "AI might eventually surpass human intelligence in specific domains, but general superintelligence remains uncertain."
    
    # Test with different metadata confidence levels
    high_confidence_result = validator.validate(
        question, 
        uncertain_answer,
        {"confidence": 0.9}
    )
    
    low_confidence_result = validator.validate(
        question, 
        uncertain_answer,
        {"confidence": 0.5}
    )
    
    # Verify that metadata influences validation
    assert high_confidence_result.criteria_scores["uncertainty"] < 1.0, \
        "High claimed confidence should penalize uncertain language"
    
    assert low_confidence_result.criteria_scores["uncertainty"] >= 0.8, \
        "Low claimed confidence should accept uncertain language"

def test_validation_source_checking():
    """Test validation of sources in answers"""
    validator = AnswerValidator()
    
    # Test factual answer with and without sources
    question = "What is the population of Tokyo?"
    
    with_source = "The population of Tokyo is approximately 14 million people (Source: Tokyo Metropolitan Government, 2023)."
    without_source = "The population of Tokyo is approximately 14 million people."
    
    # Validate both
    with_source_result = validator.validate(question, with_source)
    without_source_result = validator.validate(question, without_source)
    
    # Verify source validation
    assert with_source_result.criteria_scores["sources"] > without_source_result.criteria_scores["sources"], \
        "Answer with source should score higher on sources criterion"

@pytest.mark.asyncio
async def test_validation_system_integration():
    """Test integration of validation system with reasoning"""
    # Import orchestrator here to avoid circular imports
    from reasoning.orchestrator import reasoning_orchestrator
    
    # Test reasoning with validation
    question = "What is the melting point of iron?"
    
    # Mock final validation to isolate test
    with patch.object(reasoning_orchestrator, '_final_validation') as mock_validate:
        # Configure mock to call actual validation function
        async def side_effect(result):
            # Add validation results
            result["validation"] = await validate_complex(
                question=question,
                answer=result["answer"],
                confidence=result["confidence"]
            )
            return result
        
        mock_validate.side_effect = side_effect
        
        # Execute reasoning with validation
        result = await reasoning_orchestrator.reason(question)
        
        # Verify validation integration
        assert "validation" in result
        assert "valid" in result["validation"]
        assert "confidence" in result["validation"]

def test_validation_error_handling():
    """Test validation system error handling"""
    validator = AnswerValidator()
    
    # Test with empty inputs
    empty_result = validator.validate("", "")
    assert not empty_result.valid, "Empty inputs should be invalid"
    assert empty_result.confidence == 0.0, "Empty inputs should have zero confidence"
    
    # Test with None inputs
    try:
        none_result = validator.validate(None, None)
        # If it doesn't raise, ensure invalid result
        assert not none_result.valid
    except Exception as e:
        # Or exception is acceptable
        pass

@pytest.mark.parametrize("criteria_name", ["relevance", "completeness", "uncertainty", "sources"])
def test_individual_validation_criteria(criteria_name):
    """Test each validation criterion independently"""
    validator = AnswerValidator()
    
    # Find the criterion by name
    criterion = next((c for c in validator.criteria if c.name == criteria_name), None)
    assert criterion is not None, f"Criterion {criteria_name} not found"
    
    # Test criterion with good example
    good_examples = {
        "relevance": ("What is quantum computing?", "Quantum computing uses quantum mechanics principles for computation."),
        "completeness": ("What is photosynthesis?", "Photosynthesis is the process by which plants convert light energy into chemical energy. This process occurs in the chloroplasts and involves multiple steps including light-dependent and light-independent reactions."),
        "uncertainty": ("Will AI replace all jobs?", "AI may replace some jobs, but it's uncertain whether it will replace all jobs. Many roles requiring human creativity and empathy might remain."),
        "sources": ("Who invented the telephone?", "Alexander Graham Bell is credited with inventing the telephone in 1876 (Source: U.S. Patent Office, Patent 174,465).")
    }
    
    # Test criterion with bad example
    bad_examples = {
        "relevance": ("What is quantum computing?", "The GDP of France grew by 2.5% last year."),
        "completeness": ("What is photosynthesis?", "Plants."),
        "uncertainty": ("Will AI replace all jobs?", "AI will definitely replace all human jobs by 2030."),
        "sources": ("Who invented the telephone?", "Someone invented the telephone a long time ago.")
    }
    
    # Test good example
    good_question, good_answer = good_examples[criteria_name]
    good_score, _ = criterion.check(good_question, good_answer, None)
    
    # Test bad example
    bad_question, bad_answer = bad_examples[criteria_name]
    bad_score, _ = criterion.check(bad_question, bad_answer, None)
    
    # Verify scoring
    assert good_score > 0.7, f"Good example should score well on {criteria_name}"
    assert bad_score < 0.7, f"Bad example should score poorly on {criteria_name}"
    assert good_score > bad_score, f"Good example should score better than bad example for {criteria_name}"
