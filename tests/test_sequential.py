import pytest
from ..reasoning.sequential import SequentialReasoner

@pytest.mark.asyncio
async def test_sequential_reasoning():
    reasoner = SequentialReasoner()
    question = "What is the capital of France?"
    
    result = await reasoner.reason(question)
    
    assert "answer" in result
    assert "confidence" in result
    assert "reasoning_steps" in result
    assert len(result["reasoning_steps"]) > 0
    assert result["confidence"] >= 0.0
    assert result["confidence"] <= 1.0

@pytest.mark.asyncio
async def test_sequential_reasoning_empty_question():
    reasoner = SequentialReasoner()
    question = ""
    
    result = await reasoner.reason(question)
    
    assert result["confidence"] < 0.5  # Should have low confidence for empty question
