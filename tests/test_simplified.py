"""
Simplified tests for basic functionality validation
"""

import pytest
import asyncio
import sys
import os

# Add the project root to the path to make our mock modules importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reasoning.mock import reasoning_orchestrator, ReasoningStrategy
from validators.mock import validate_complex, review_answer
from research.mock import research_integrator

@pytest.mark.asyncio
async def test_reasoning_basic():
    """Test basic reasoning functionality"""
    question = "What is the capital of France?"
    result = await reasoning_orchestrator.reason(question)
    
    # Verify basic structure
    assert "answer" in result
    assert "confidence" in result
    assert "reasoning_steps" in result
    assert "metadata" in result
    
    # Verify values
    assert len(result["answer"]) > 0
    assert result["confidence"] > 0
    assert len(result["reasoning_steps"]) > 0
    
    print(f"Successfully tested basic reasoning with result: {result}")

@pytest.mark.asyncio
async def test_empty_question():
    """Test error handling for empty questions"""
    try:
        await reasoning_orchestrator.reason("")
        assert False, "Should have raised ValueError"
    except ValueError:
        # Expected
        pass
    
    print("Successfully tested error handling for empty questions")

@pytest.mark.asyncio
async def test_validation():
    """Test validation functionality"""
    result = await validate_complex(
        "What is quantum computing?",
        "Quantum computing is a type of computing that uses quantum mechanics to perform computations."
    )
    
    # Verify validation structure
    assert "valid" in result
    assert "confidence" in result
    assert "validation_details" in result
    
    # Verify values
    assert result["valid"]
    assert result["confidence"] > 0.5
    
    print(f"Successfully tested validation with result: {result}")

@pytest.mark.asyncio
async def test_research():
    """Test research functionality"""
    context = await research_integrator.research("What is machine learning?")
    
    # Verify context structure
    assert hasattr(context, "original_query")
    assert hasattr(context, "processed_queries")
    assert hasattr(context, "search_results")
    assert hasattr(context, "confidence")
    
    # Verify values
    assert context.original_query == "What is machine learning?"
    assert len(context.processed_queries) > 0
    assert len(context.search_results) > 0
    assert context.confidence > 0
    
    print(f"Successfully tested research with result: {context}")

@pytest.mark.asyncio
async def test_reviewer():
    """Test reviewer functionality"""
    result = await review_answer(
        "Explain how neural networks function",
        "Neural networks are computational models inspired by the human brain that process information through interconnected nodes."
    )
    
    # Verify reviewer structure
    assert "approved" in result
    assert "confidence" in result
    assert "feedback" in result
    assert "suggestions" in result
    
    # Verify values
    assert result["approved"]
    assert result["confidence"] > 0.5
    
    print(f"Successfully tested reviewer with result: {result}")


# If running this file directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
