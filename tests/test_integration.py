"""Tests for reasoning and validation integration"""

import pytest
from ..integration.reasoning_validator import (
    ReasoningValidator,
    ReasoningFeedback,
    ValidationFeedback
)
from ..validators.enhanced_validator import ValidationLevel, ValidationAspect

@pytest.fixture
def integration():
    """Create integration instance"""
    return ReasoningValidator()

@pytest.mark.asyncio
async def test_strategy_selection(integration):
    """Test initial strategy selection"""
    # Test logical pattern
    question1 = "If all humans are mortal, and Socrates is human, what can we conclude?"
    strategy1 = integration._select_initial_strategy(question1, None)
    assert strategy1 == "logical"
    
    # Test abductive pattern
    question2 = "Why does the sky appear blue?"
    strategy2 = integration._select_initial_strategy(question2, None)
    assert strategy2 == "abductive"
    
    # Test creative pattern
    question3 = "What are some creative ways to reduce plastic waste?"
    strategy3 = integration._select_initial_strategy(question3, None)
    assert strategy3 == "lateral"
    
    # Test complex pattern
    question4 = "What are the causes, effects, and potential solutions for climate change?"
    strategy4 = integration._select_initial_strategy(question4, None)
    assert strategy4 == "branching"

@pytest.mark.asyncio
async def test_validation_config(integration):
    """Test validation configuration creation"""
    # Test basic question
    question1 = "What is the capital of France?"
    config1 = integration._create_validation_config(question1, None)
    assert config1.level == ValidationLevel.BASIC
    assert ValidationAspect.COMPLETENESS in config1.required_aspects
    
    # Test complex question
    question2 = "What are the major economic, social, and environmental impacts of urbanization?"
    config2 = integration._create_validation_config(question2, None)
    assert config2.level == ValidationLevel.STRICT
    assert ValidationAspect.REASONING in config2.required_aspects
    
    # Test with context
    context = {
        "validation_level": "expert",
        "min_confidence": 0.9,
        "domain": "physics"
    }
    config3 = integration._create_validation_config("test", context)
    assert config3.level == ValidationLevel.EXPERT
    assert config3.min_confidence == 0.9
    assert config3.domain == "physics"

@pytest.mark.asyncio
async def test_strategy_adjustment(integration):
    """Test strategy adjustment based on feedback"""
    # Test logical fallacy issue
    feedback1 = ReasoningFeedback(
        confidence=0.5,
        issues=["logical fallacy detected"],
        suggestions=[],
        aspect_scores={"reasoning": 0.4},
        requires_revision=True
    )
    new_strategy1 = integration._adjust_strategy("sequential", feedback1, 1)
    assert new_strategy1 == "logical"
    
    # Test creativity suggestion
    feedback2 = ReasoningFeedback(
        confidence=0.6,
        issues=[],
        suggestions=["need more creative approach"],
        aspect_scores={"creativity": 0.5},
        requires_revision=True
    )
    new_strategy2 = integration._adjust_strategy("sequential", feedback2, 1)
    assert new_strategy2 == "lateral"
    
    # Test evidence issue
    feedback3 = ReasoningFeedback(
        confidence=0.5,
        issues=[],
        suggestions=["provide supporting evidence"],
        aspect_scores={"reasoning": 0.7, "evidence": 0.4},
        requires_revision=True
    )
    new_strategy3 = integration._adjust_strategy("sequential", feedback3, 1)
    assert new_strategy3 == "abductive"

@pytest.mark.asyncio
async def test_strategy_performance_tracking(integration):
    """Test strategy performance tracking"""
    # Update with successful result
    integration._update_strategy_performance("logical", 0.8)
    perf1 = integration.strategy_performance["logical"]
    assert perf1["success_count"] == 1
    assert perf1["total_count"] == 1
    assert perf1["avg_confidence"] == 0.8
    
    # Update with unsuccessful result
    integration._update_strategy_performance("logical", 0.5)
    perf2 = integration.strategy_performance["logical"]
    assert perf2["success_count"] == 1
    assert perf2["total_count"] == 2
    assert 0.6 < perf2["avg_confidence"] < 0.7

@pytest.mark.asyncio
async def test_full_integration_process(integration):
    """Test complete integration process"""
    # Test with simple question
    result1 = await integration.process(
        "What is the capital of France?",
        {"validation_level": "basic"}
    )
    assert "answer" in result1
    assert "confidence" in result1
    assert "reasoning_steps" in result1
    assert "validation" in result1
    
    # Test with complex question
    result2 = await integration.process(
        "Why does quantum entanglement occur?",
        {
            "validation_level": "strict",
            "domain": "physics",
            "min_confidence": 0.8
        }
    )
    assert result2["confidence"] >= 0.8
    assert len(result2["reasoning_steps"]) > 1
    assert "aspects" in result2["validation"]

@pytest.mark.asyncio
async def test_feedback_loop(integration):
    """Test feedback loop between reasoning and validation"""
    # Create initial feedback
    validation_feedback = ValidationFeedback(
        strategy_used="sequential",
        reasoning_steps=[
            {"step": "initial", "output": "first attempt"}
        ],
        evidence=["source1"],
        context={"domain": "physics"}
    )
    
    # Validate with feedback
    validation_result = await integration._validate_with_feedback(
        "How does gravity work?",
        "Gravity is a fundamental force of nature.",
        integration._create_validation_config(
            "How does gravity work?",
            {"domain": "physics"}
        ),
        validation_feedback
    )
    
    # Create reasoning feedback
    reasoning_feedback = ReasoningFeedback(
        confidence=validation_result.confidence,
        issues=validation_result.issues,
        suggestions=validation_result.suggestions,
        aspect_scores={k.value: v for k, v in validation_result.aspects.items()},
        requires_revision=validation_result.confidence < 0.7
    )
    
    # Test feedback handling
    assert reasoning_feedback.requires_revision  # Should require revision as answer is too simple
    new_strategy = integration._adjust_strategy("sequential", reasoning_feedback, 1)
    assert new_strategy != "sequential"  # Should change strategy

@pytest.mark.asyncio
async def test_error_handling(integration):
    """Test error handling in integration"""
    # Test with invalid question
    with pytest.raises(Exception):
        await integration.process("")
    
    # Test with excessive attempts
    context = {
        "validation_level": "expert",
        "min_confidence": 0.99  # Unreasonably high
    }
    with pytest.raises(Exception) as exc_info:
        await integration.process("test question", context)
    assert "Failed to generate satisfactory answer" in str(exc_info.value)

@pytest.mark.asyncio
async def test_result_combination(integration):
    """Test combining results from reasoning and validation"""
    reasoning_result = {
        "answer": "Test answer",
        "reasoning_steps": [{"step": "test", "output": "test"}],
        "metadata": {"strategy": "logical"}
    }
    
    validation_result = ValidationResult(
        valid=True,
        confidence=0.8,
        aspects={ValidationAspect.COMPLETENESS: 0.8},
        issues=[],
        suggestions=[],
        metadata={"validation_level": "strict"}
    )
    
    combined = integration._combine_results(reasoning_result, validation_result)
    
    assert combined["answer"] == reasoning_result["answer"]
    assert combined["confidence"] == validation_result.confidence
    assert "validation" in combined
    assert "metadata" in combined
    assert "strategy_performance" in combined["metadata"]

@pytest.mark.asyncio
async def test_validation_with_context(integration):
    """Test validation with different contexts"""
    # Test with domain context
    result1 = await integration.process(
        "What is the speed of light?",
        {"domain": "physics"}
    )
    assert result1["validation"]["aspects"].get("domain", 0) > 0.7
    
    # Test with previous answers
    result2 = await integration.process(
        "Why is this important?",
        {
            "previous_answers": [
                "The speed of light is a fundamental constant.",
                "It defines the maximum speed in the universe."
            ]
        }
    )
    assert result2["validation"]["aspects"].get("consistency", 0) > 0.6