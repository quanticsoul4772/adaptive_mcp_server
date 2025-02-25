"""
End-to-End Tests for Adaptive MCP Server

These tests validate the complete flow from input to output,
exercising all components in realistic scenarios.
"""

import pytest
import asyncio
import logging
from typing import Dict, Any, List

# Import server components
from reasoning.mock import reasoning_orchestrator, ReasoningStrategy
from research.mock import research_integrator
from validators.mock import validate_complex, review_answer

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test.e2e")

# Test scenarios representing different question types
SCENARIOS = [
    {
        "name": "factual_query",
        "question": "What is quantum computing?",
        "expected_strategies": ["SEQUENTIAL", "ABDUCTIVE"],
        "expected_content": ["quantum", "computer", "superposition"],
        "min_confidence": 0.7
    },
    {
        "name": "analytical_query",
        "question": "Compare renewable energy sources and their environmental impacts",
        "expected_strategies": ["BRANCHING", "LOGICAL"],
        "expected_content": ["solar", "wind", "hydro", "impact", "environment"],
        "min_confidence": 0.6
    },
    {
        "name": "creative_query",
        "question": "Propose an innovative solution to urban traffic congestion",
        "expected_strategies": ["LATERAL", "BRANCHING"],
        "expected_content": ["traffic", "urban", "solution", "innovation"],
        "min_confidence": 0.5
    },
    {
        "name": "logical_query",
        "question": "If all mammals are warm-blooded, and whales are mammals, what can we conclude about whales?",
        "expected_strategies": ["LOGICAL", "SEQUENTIAL"],
        "expected_content": ["warm-blooded", "mammal", "whale", "conclude"],
        "min_confidence": 0.8
    },
    {
        "name": "research_heavy_query",
        "question": "What are the latest developments in CRISPR gene editing technology?",
        "expected_strategies": ["SEQUENTIAL", "ABDUCTIVE"],
        "expected_content": ["CRISPR", "gene", "editing", "technology"],
        "min_confidence": 0.6
    }
]

@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["name"] for s in SCENARIOS])
async def test_end_to_end_scenario(scenario):
    """
    Test end-to-end processing of different question types
    
    Args:
        scenario: Test scenario with question and expectations
    """
    logger.info(f"Testing scenario: {scenario['name']}")
    logger.info(f"Question: {scenario['question']}")
    
    # Process the question through the full pipeline
    try:
        result = await reasoning_orchestrator.reason(scenario["question"])
        
        # Log detailed results for debugging
        logger.info(f"Got result with confidence: {result.get('confidence', 0)}")
        logger.info(f"Answer: {result.get('answer', '')[:100]}...")
        
        # Basic structure assertions
        assert "answer" in result, "Result missing 'answer' field"
        assert "confidence" in result, "Result missing 'confidence' field"
        assert "reasoning_steps" in result, "Result missing 'reasoning_steps' field"
        assert "metadata" in result, "Result missing 'metadata' field"
        
        # Content assertions
        answer = result["answer"].lower()
        for expected_term in scenario["expected_content"]:
            assert expected_term.lower() in answer, f"Expected term '{expected_term}' not found in answer"
        
        # Strategy assertions
        if "strategies_used" in result["metadata"]:
            strategies_used = result["metadata"]["strategies_used"]
            assert any(expected in str(strategies_used) for expected in scenario["expected_strategies"]), \
                f"None of the expected strategies {scenario['expected_strategies']} found in {strategies_used}"
        
        # Confidence assertions
        assert result["confidence"] >= scenario["min_confidence"], \
            f"Confidence {result['confidence']} below minimum {scenario['min_confidence']}"
        
        # Reasoning steps assertions
        assert len(result["reasoning_steps"]) >= 2, "Expected at least 2 reasoning steps"
        
        # Validate steps have required structure
        for step in result["reasoning_steps"]:
            assert "step" in step, "Reasoning step missing 'step' field"
            assert "output" in step, "Reasoning step missing 'output' field"
        
        logger.info(f"Scenario {scenario['name']} passed!")
    
    except Exception as e:
        logger.error(f"Error in scenario {scenario['name']}: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_error_handling_scenarios():
    """Test how the system handles various error conditions"""
    # Test empty input
    with pytest.raises(ValueError, match="Question cannot be empty"):
        await reasoning_orchestrator.reason("")
    
    # Test very short/simple query
    result = await reasoning_orchestrator.reason("Hi")
    assert result["confidence"] < 0.8, "Very simple queries should have lower confidence"
    
    # Test extremely long query (potential overload)
    long_question = "Why? " * 500
    result = await reasoning_orchestrator.reason(long_question)
    assert "answer" in result, "System should handle very long questions"
    
    # Test ambiguous query
    ambiguous_result = await reasoning_orchestrator.reason("Why?")
    assert ambiguous_result["confidence"] < 0.7, "Ambiguous questions should have lower confidence"
    
    # Test non-sensical query
    nonsense_result = await reasoning_orchestrator.reason("Colorless green ideas sleep furiously")
    assert nonsense_result["confidence"] < 0.5, "Non-sensical questions should have very low confidence"

@pytest.mark.asyncio
async def test_complex_reasoning_chain():
    """Test a complex multi-step reasoning process with research"""
    complex_question = "What might be the economic and social implications of widespread quantum computing adoption?"
    
    # Process through full pipeline
    result = await reasoning_orchestrator.reason(complex_question)
    
    # Validate comprehensive response
    assert len(result["answer"]) > 200, "Expected detailed answer for complex question"
    assert result["confidence"] > 0.6, "Expected reasonable confidence for complex question"
    assert len(result["reasoning_steps"]) >= 3, "Expected at least 3 steps for complex reasoning"
    
    # Check for both economic and social aspects
    answer = result["answer"].lower()
    assert "economic" in answer, "Expected economic analysis in answer"
    assert "social" in answer, "Expected social analysis in answer"
    
    # Check that multiple reasoning strategies were used
    if "strategies_used" in result["metadata"]:
        strategies = result["metadata"]["strategies_used"]
        assert len(strategies) >= 2, "Expected at least 2 strategies for complex question"

@pytest.mark.asyncio
async def test_research_integration():
    """Test specific research integration capabilities"""
    research_question = "What are the latest advancements in fusion energy research?"
    
    # Get research context directly
    research_context = await research_integrator.research(research_question)
    
    # Validate research results
    assert research_context.confidence > 0, "Expected non-zero research confidence"
    assert len(research_context.search_results) > 0, "Expected at least one search result"
    assert len(research_context.processed_queries) > 0, "Expected at least one processed query"
    
    # Now test integration with reasoning
    result = await reasoning_orchestrator.reason(research_question)
    
    # Verify research elements in answer
    assert "research" in str(result["metadata"]), "Expected research metadata"
    assert len(result["reasoning_steps"]) >= 2, "Expected research step in reasoning"

@pytest.mark.asyncio
async def test_multi_strategy_orchestration():
    """Test specifically how multiple strategies work together"""
    question = "How might quantum computing affect blockchain security, and what adaptations might be needed?"
    
    # Process through orchestrator
    result = await reasoning_orchestrator.reason(question)
    
    # Verify multiple strategies used
    if "strategies_used" in result["metadata"]:
        strategies = result["metadata"]["strategies_used"]
        assert len(strategies) >= 2, "Expected multiple strategies"
        
        # Check for expected strategy combinations
        strategy_types = set(strategies)
        assert len(strategy_types) >= 2, "Expected at least 2 different strategy types"
    
    # Verify comprehensive answer covering both aspects of the question
    answer = result["answer"].lower()
    assert "quantum" in answer, "Expected quantum computing analysis"
    assert "blockchain" in answer, "Expected blockchain analysis"
    assert "security" in answer, "Expected security analysis"
    assert any(term in answer for term in ["adapt", "adaptation", "solution"]), "Expected adaptation discussion"

@pytest.mark.asyncio
async def test_validation_system():
    """Test specifically the validation capabilities"""
    question = "What causes seasons on Earth?"
    answer = "Seasons are caused by the Earth's tilted axis as it orbits the Sun."
    
    # Perform validation
    validation_result = await validate_complex(question, answer, confidence=0.9)
    
    # Verify validation structure
    assert "valid" in validation_result, "Expected 'valid' in validation result"
    assert "confidence" in validation_result, "Expected 'confidence' in validation result"
    assert "explanation" in validation_result, "Expected 'explanation' in validation result"
    
    # Verify validation logic
    assert validation_result["valid"], "Expected valid result for correct answer"
    assert validation_result["confidence"] > 0.8, "Expected high confidence for valid answer"
    
    # Test validation with incorrect answer
    wrong_answer = "Seasons are caused by the Earth's varying distance from the Sun."
    wrong_validation = await validate_complex(question, wrong_answer, confidence=0.9)
    
    # Should be marked as invalid or have low confidence
    assert not wrong_validation["valid"] or wrong_validation["confidence"] < 0.5, \
        "Expected invalid result or low confidence for incorrect answer"
