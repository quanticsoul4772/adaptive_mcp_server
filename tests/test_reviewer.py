"""Tests for the AI self-review module"""

import pytest
from ..validators.reviewer import (
    AnswerReviewer,
    ReviewCriterion,
    ReviewFinding,
    ReviewResult
)

def test_reviewer_initialization():
    """Test reviewer initialization"""
    reviewer = AnswerReviewer()
    assert len(reviewer.criteria_weights) == 5
    assert sum(reviewer.criteria_weights.values()) == pytest.approx(1.0)

def test_question_component_extraction():
    """Test extraction of question components"""
    reviewer = AnswerReviewer()
    
    # Test simple question
    components = reviewer._extract_question_components(
        "What is the capital of France?"
    )
    assert "capital" in components
    assert "france" in components
    
    # Test compound question
    components = reviewer._extract_question_components(
        "What are the causes and effects of climate change?"
    )
    assert len(components) >= 2
    assert any("cause" in c for c in components)
    assert any("effect" in c for c in components)

def test_text_similarity():
    """Test text similarity calculation"""
    reviewer = AnswerReviewer()
    
    # Test identical texts
    score = reviewer._calculate_text_similarity(
        "The sky is blue",
        "The sky is blue"
    )
    assert score == 1.0
    
    # Test different texts
    score = reviewer._calculate_text_similarity(
        "The sky is blue",
        "Grass is green"
    )
    assert score < 0.3
    
    # Test partially similar texts
    score = reviewer._calculate_text_similarity(
        "The sky is blue",
        "The sky was blue yesterday"
    )
    assert 0.3 < score < 1.0

def test_contradiction_detection():
    """Test contradiction detection"""
    reviewer = AnswerReviewer()
    
    # Test direct contradiction
    assert reviewer._contradicts(
        "The sky is blue",
        "The sky is not blue"
    )
    
    # Test non-contradiction
    assert not reviewer._contradicts(
        "The sky is blue",
        "The ocean is blue"
    )
    
    # Test complex contradiction
    assert reviewer._contradicts(
        "All birds can fly",
        "Some birds are not able to fly"
    )

def test_clarity_check():
    """Test clarity assessment"""
    reviewer = AnswerReviewer()
    
    # Test clear answer
    clear_finding = reviewer._check_clarity(
        "The Earth orbits the Sun. This takes one year."
    )
    assert clear_finding.score > 0.7
    assert not clear_finding.suggestions
    
    # Test unclear answer
    unclear_finding = reviewer._check_clarity(
        "The supercalifragilisticexpialidocious phenomenon manifests through extraordinarily complicated mechanisms that perpetuate indefinitely."
    )
    assert unclear_finding.score < 0.7
    assert len(unclear_finding.suggestions) > 0

def test_consistency_check():
    """Test consistency checking"""
    reviewer = AnswerReviewer()
    
    # Test consistent answer
    consistent_finding = reviewer._check_consistency(
        "Water freezes at 0°C. Ice melts at 0°C.",
        None
    )
    assert consistent_finding.score > 0.8
    
    # Test inconsistent answer
    inconsistent_finding = reviewer._check_consistency(
        "The event happened in 1999. No, actually it was in 2001.",
        None
    )
    assert inconsistent_finding.score < 0.8
    assert any("contradiction" in s.lower() for s in inconsistent_finding.suggestions)

@pytest.mark.asyncio
async def test_completeness_check():
    """Test completeness checking"""
    reviewer = AnswerReviewer()
    
    # Test complete answer
    complete_finding = await reviewer._check_completeness(
        "What are the colors of the rainbow?",
        "The rainbow has seven colors: red, orange, yellow, green, blue, indigo, and violet."
    )
    assert complete_finding.score > 0.8
    
    # Test incomplete answer
    incomplete_finding = await reviewer._check_completeness(
        "What are the colors of the rainbow?",
        "The rainbow is colorful."
    )
    assert incomplete_finding.score < 0.6
    assert len(incomplete_finding.suggestions) > 0

@pytest.mark.asyncio
async def test_relevance_check():
    """Test relevance checking"""
    reviewer = AnswerReviewer()
    
    # Test relevant answer
    relevant_finding = await reviewer._check_relevance(
        "What is photosynthesis?",
        "Photosynthesis is the process by which plants convert sunlight into energy, producing oxygen as a byproduct."
    )
    assert relevant_finding.score > 0.6
    
    # Test irrelevant answer
    irrelevant_finding = await reviewer._check_relevance(
        "What is photosynthesis?",
        "The weather is nice today."
    )
    assert irrelevant_finding.score < 0.4
    assert len(irrelevant_finding.suggestions) > 0

@pytest.mark.asyncio
async def test_accuracy_check():
    """Test accuracy checking"""
    reviewer = AnswerReviewer()
    
    # Test accurate answer
    accurate_finding = await reviewer._check_accuracy(
        "What is the capital of France?",
        "Paris is the capital of France."
    )
    assert accurate_finding.score > 0.7
    
    # Test inaccurate answer
    inaccurate_finding = await reviewer._check_accuracy(
        "What is the capital of France?",
        "London is the capital of France."
    )
    assert inaccurate_finding.score < 0.5
    assert any("contradiction" in s.lower() for s in inaccurate_finding.suggestions)

@pytest.mark.asyncio
async def test_full_review():
    """Test complete review process"""
    reviewer = AnswerReviewer()
    
    # Test good answer
    good_result = await reviewer.review(
        "What is the speed of light?",
        "The speed of light in a vacuum is approximately 299,792,458 meters per second. This is a fundamental constant in physics."
    )
    assert good_result.overall_score > 0.7
    assert not good_result.needs_revision
    
    # Test poor answer
    poor_result = await reviewer.review(
        "What is the speed of light?",
        "It's really fast."
    )
    assert poor_result.overall_score < 0.7
    assert poor_result.needs_revision
    assert len(poor_result.revision_suggestions) > 0

@pytest.mark.asyncio
async def test_error_handling():
    """Test review error handling"""
    reviewer = AnswerReviewer()
    
    # Test with empty inputs
    with pytest.raises(Exception):
        await reviewer.review("", "")
    
    # Test with invalid inputs
    with pytest.raises(Exception):
        await reviewer.review("   ", "   ")
        
    # Test with missing context
    result = await reviewer.review(
        "Test question?",
        "Test answer.",
        None
    )
    assert isinstance(result, ReviewResult)

@pytest.mark.asyncio
async def test_context_handling():
    """Test handling of context in review"""
    reviewer = AnswerReviewer()
    
    context = {
        "previous_answers": [
            "The Earth orbits the Sun.",
            "A year is 365 days."
        ]
    }
    
    # Test consistent with context
    consistent_result = await reviewer.review(
        "How long is a year?",
        "A year is approximately 365 days, the time it takes Earth to orbit the Sun.",
        context
    )
    assert consistent_result.overall_score > 0.7
    
    # Test inconsistent with context
    inconsistent_result = await reviewer.review(
        "How long is a year?",
        "A year is 400 days.",
        context
    )
    assert inconsistent_result.overall_score < 0.7
    assert any("conflict" in s.lower() for s in inconsistent_result.revision_suggestions)
