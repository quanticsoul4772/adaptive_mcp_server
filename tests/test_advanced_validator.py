"""Tests for the advanced validation module"""

import pytest
from ..validators.advanced_validator import (
    AdvancedValidator,
    ValidationReason,
    ValidationRule
)

@pytest.fixture
def validator():
    """Create validator instance"""
    return AdvancedValidator()

@pytest.mark.asyncio
async def test_semantic_coherence(validator):
    """Test semantic coherence checking"""
    # Test highly coherent Q&A
    coherent_result = await validator._check_semantic_coherence(
        "What is photosynthesis?",
        "Photosynthesis is the process by which plants convert sunlight into energy.",
        None
    )
    assert coherent_result.score > 0.7
    assert not coherent_result.suggestions
    
    # Test incoherent Q&A
    incoherent_result = await validator._check_semantic_coherence(
        "What is photosynthesis?",
        "The weather is nice today.",
        None
    )
    assert incoherent_result.score < 0.5
    assert len(incoherent_result.suggestions) > 0

@pytest.mark.asyncio
async def test_factual_support(validator):
    """Test factual support verification"""
    # Test well-supported answer
    supported_result = await validator._check_factual_support(
        "What is the capital of France?",
        "Paris is the capital of France. It has been since 987 CE.",
        None
    )
    assert supported_result.score > 0.7
    
    # Test unsupported answer
    unsupported_result = await validator._check_factual_support(
        "What is the capital of France?",
        "I think it might be somewhere in Europe.",
        None
    )
    assert unsupported_result.score < 0.6
    assert "sources" in unsupported_result.suggestions[0]

@pytest.mark.asyncio
async def test_style_quality(validator):
    """Test style quality assessment"""
    # Test good style
    good_style = await validator._check_style_quality(
        "How does gravity work?",
        "Gravity is a fundamental force that attracts objects with mass. It helps keep planets in orbit.",
        None
    )
    assert good_style.score > 0.7
    assert not good_style.suggestions
    
    # Test poor style
    poor_style = await validator._check_style_quality(
        "How does gravity work?",
        "The gravitational forces being exerted upon massive celestial bodies are being constantly observed to be directly proportional to their extraordinarily large masses.",
        None
    )
    assert poor_style.score < 0.7
    assert any("complex" in s.lower() for s in poor_style.suggestions)

@pytest.mark.asyncio
async def test_source_credibility(validator):
    """Test source credibility evaluation"""
    # Test credible sources
    credible = await validator._check_source_credibility(
        "What causes climate change?",
        "According to NASA (nasa.gov), greenhouse gases are a major factor. The EPA (epa.gov) reports increasing CO2 levels.",
        None
    )
    assert credible.score > 0.8
    
    # Test questionable sources
    questionable = await validator._check_source_credibility(
        "What causes climate change?",
        "According to randomwebsite.com, it's all a myth.",
        None
    )
    assert questionable.score < 0.6

@pytest.mark.asyncio
async def test_context_consistency(validator):
    """Test context consistency checking"""
    context = {
        "previous_answers": [
            "Gravity is a fundamental force of nature.",
            "Einstein described gravity in general relativity."
        ],
        "domain": "physics"
    }
    
    # Test consistent answer
    consistent = await validator._check_context_consistency(
        "How does gravity affect time?",
        "According to general relativity, gravity can warp spacetime, affecting the passage of time.",
        context
    )
    assert consistent.score > 0.8
    
    # Test inconsistent answer
    inconsistent = await validator._check_context_consistency(
        "How does gravity affect time?",
        "Gravity has nothing to do with time.",
        context
    )
    assert inconsistent.score < 0.5

def test_factual_claim_detection(validator):
    """Test factual claim detection"""
    # Test clear factual claim
    assert validator._is_factual_claim(
        "Water boils at 100 degrees Celsius."
    )
    
    # Test opinion
    assert not validator._is_factual_claim(
        "I think water is interesting."
    )

def test_complex_word_detection(validator):
    """Test complex word detection"""
    # Test with complex words
    assert validator._has_complex_words(
        "The supercalifragilisticexpialidocious phenomenon."
    )
    
    # Test without complex words
    assert not validator._has_complex_words(
        "The cat sat on the mat."
    )

def test_source_extraction(validator):
    """Test source reference extraction"""
    text = """According to NASA, the moon orbits Earth.
    Smith (2020) suggests this has been known for centuries.
    [Source: Encyclopedia Britannica]"""
    
    sources = validator._extract_sources(text)
    assert len(sources) == 3
    assert "NASA" in sources
    assert "Smith" in sources
    assert "Encyclopedia Britannica" in sources

@pytest.mark.asyncio
async def test_full_validation_process(validator):
    """Test complete validation process"""
    question = "What is the theory of relativity?"
    answer = """According to Einstein (physics.org), relativity describes how space and time are connected.
    The theory has been extensively tested and verified by numerous experiments.
    This fundamental principle of physics helps us understand the universe."""
    
    context = {
        "domain": "physics",
        "previous_answers": [
            "Physics helps us understand the universe.",
            "Einstein revolutionized our understanding of space and time."
        ]
    }
    
    result = await validator.validate(question, answer, context)
    
    # Check structure
    assert "valid" in result
    assert "confidence" in result
    assert "reasons" in result
    assert "suggestions" in result
    assert "metadata" in result
    
    # Check scores
    assert result["confidence"] > 0
    assert all(0 <= reason["score"] <= 1 for reason in result["reasons"])
    
    # Check completeness
    expected_aspects = {
        "semantic_coherence", "factual_support", "style_quality",
        "source_credibility", "context_consistency"
    }
    actual_aspects = {reason["aspect"] for reason in result["reasons"]}
    assert expected_aspects == actual_aspects

@pytest.mark.asyncio
async def test_error_handling(validator):
    """Test error handling in validation"""
    # Test with invalid inputs
    with pytest.raises(Exception):
        await validator.validate("", "", None)
    
    with pytest.raises(Exception):
        await validator.validate("Question?", None, None)
    
    # Test with malformed context
    with pytest.raises(Exception):
        await validator.validate(
            "Question?",
            "Answer.",
            "invalid context"  # Should be dict
        )
