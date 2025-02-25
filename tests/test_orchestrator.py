"""
Comprehensive Tests for Reasoning Orchestrator with Research Integration
"""

import pytest
import asyncio
from reasoning.orchestrator import reasoning_orchestrator, ReasoningStrategy

@pytest.mark.asyncio
async def test_orchestrator_basic_reasoning():
    """
    Test basic reasoning with research integration
    """
    question = "What is the capital of France?"
    result = await reasoning_orchestrator.reason(question)
    
    assert 'answer' in result
    assert 'confidence' in result
    assert result['confidence'] > 0
    assert len(result['answer']) > 0
    assert 'reasoning_steps' in result
    assert 'metadata' in result

@pytest.mark.asyncio
async def test_orchestrator_complex_question():
    """
    Test reasoning with a more complex question
    """
    question = "Explain the long-term environmental impacts of renewable energy technologies"
    result = await reasoning_orchestrator.reason(question)
    
    assert 'answer' in result
    assert 'confidence' in result
    assert result['confidence'] > 0
    assert len(result['answer']) > 0
    assert len(result['reasoning_steps']) > 0
    
    # Check for research integration
    metadata = result.get('metadata', {})
    assert 'strategies_used' in metadata
    assert len(metadata['strategies_used']) > 0

@pytest.mark.asyncio
async def test_orchestrator_creative_question():
    """
    Test reasoning with a creative thinking prompt
    """
    question = "Propose an innovative solution to urban traffic congestion"
    result = await reasoning_orchestrator.reason(question)
    
    assert 'answer' in result
    assert 'confidence' in result
    assert result['confidence'] > 0
    assert len(result['answer']) > 0
    
    # Check for lateral/creative thinking strategy
    metadata = result.get('metadata', {})
    assert 'strategies_used' in metadata
    assert any('LATERAL' in strategy for strategy in metadata['strategies_used'])

@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """
    Test orchestrator's error handling with edge cases
    """
    # Test empty question
    with pytest.raises(ValueError):
        await reasoning_orchestrator.reason("")
    
    # Test whitespace-only question
    with pytest.raises(ValueError):
        await reasoning_orchestrator.reason("   ")

@pytest.mark.asyncio
async def test_orchestrator_multi_strategy():
    """
    Test reasoning with multiple strategies
    """
    question = "How does quantum computing potentially revolutionize cryptography?"
    result = await reasoning_orchestrator.reason(question)
    
    assert 'answer' in result
    assert 'confidence' in result
    assert result['confidence'] > 0
    assert len(result['answer']) > 0
    
    # Check for multiple strategies
    metadata = result.get('metadata', {})
    assert 'strategies_used' in metadata
    assert len(metadata['strategies_used']) > 1

def test_orchestrator_singleton():
    """
    Verify that reasoning_orchestrator is a singleton
    """
    from reasoning.orchestrator import reasoning_orchestrator as first_instance
    from reasoning.orchestrator import reasoning_orchestrator as second_instance
    
    assert first_instance is second_instance, "Reasoning orchestrator should be a singleton"
