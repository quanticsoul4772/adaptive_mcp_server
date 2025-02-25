"""Tests for the answer validation module"""

import pytest
from ..validators.basic_validator import AnswerValidator, validate_answer

def test_validator_initialization():
    """Test validator initialization and criteria setup"""
    validator = AnswerValidator()
    assert len(validator.criteria) == 4
    assert sum(c.weight for c in validator.criteria) == pytest.approx(1.0)

def test_empty_inputs():
    """Test validation with empty inputs"""
    result = validate_answer("", "", None)
    assert not result["valid"]
    assert result["confidence"] == 0.0
    assert "Empty question or answer" in result["explanation"]

def test_high_confidence_answer():
    """Test validation of a high-quality answer"""
    question = "What is the capital of France?"
    answer = "According to geographical data, Paris is the capital of France. It has been the capital since 987 CE when Hugh Capet made it the seat of his power."
    metadata = {"confidence": 0.9, "sources": ["Geographic Database 2024"]}
    
    result = validate_answer(question, answer, metadata)
    
    assert result["valid"]
    assert result["confidence"] > 0.8
    assert "Strong aspects" in result["explanation"]
    assert len(result["criteria_scores"]) == 4

def test_low_quality_answer():
    """Test validation of a low-quality answer"""
    question = "What is the capital of France?"
    answer = "paris"  # Incomplete, no capitalization, no context
    
    result = validate_answer(question, answer)
    
    assert not result["valid"]
    assert result["confidence"] < 0.6
    assert any("complete sentence" in s for s in result["suggestions"])

def test_uncertainty_handling():
    """Test how validator handles uncertainty in answers"""
    validator = AnswerValidator()
    
    # Test with high confidence metadata but uncertain language
    question = "What is 2+2?"
    uncertain_answer = "It seems that 2+2 might be 4"
    result = validator.validate(question, uncertain_answer, {"confidence": 0.95})
    
    assert result.criteria_scores["uncertainty"] < 1.0
    assert any("more definitive" in s for s in result.suggestions)
    
    # Test with low confidence metadata but certain language
    certain_answer = "2+2 is definitely 4"
    result = validator.validate(question, certain_answer, {"confidence": 0.6})
    
    assert result.criteria_scores["uncertainty"] < 1.0
    assert any("uncertainty" in s.lower() for s in result.suggestions)

def test_source_validation():
    """Test source checking in answers"""
    question = "What is the speed of light?"
    
    # Answer with proper citation
    good_answer = "According to physics textbooks, the speed of light in vacuum is approximately 299,792,458 meters per second (2024)."
    result = validate_answer(question, good_answer)
    assert result["criteria_scores"]["sources"] == 1.0
    
    # Answer without citation
    bad_answer = "The speed of light is 299,792,458 meters per second."
    result = validate_answer(question, bad_answer)
    assert result["criteria_scores"]["sources"] < 1.0
    assert any("citing sources" in s.lower() for s in result["suggestions"])

def test_completeness_checking():
    """Test answer completeness validation"""
    question = "Describe the water cycle."
    
    # Complete answer
    complete_answer = "The water cycle involves evaporation from bodies of water, condensation in clouds, and precipitation back to Earth's surface."
    result = validate_answer(question, complete_answer)
    assert result["criteria_scores"]["completeness"] > 0.8
    
    # Incomplete answer
    incomplete_answer = "water goes up and down"
    result = validate_answer(question, incomplete_answer)
    assert result["criteria_scores"]["completeness"] < 0.6
    assert any("complete sentence" in s.lower() for s in result["suggestions"])
