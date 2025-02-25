"""
Comprehensive tests for the reasoning module.
"""

import pytest
from typing import Dict, Any, List
from ..reasoning.orchestrator import ReasoningOrchestrator
from mcp.types import McpError

@pytest.mark.asyncio
async def test_strategy_selection(
    orchestrator: ReasoningOrchestrator,
    sample_test_questions: List[Dict[str, Any]]
):
    """Test strategy selection for different question types"""
    for test_case in sample_test_questions:
        question = test_case["question"]
        expected_type = test_case["expected_type"]
        
        strategies = orchestrator._select_strategies(question)
        
        if expected_type == "factual":
            assert any(s.name == "SEQUENTIAL" for s in strategies)
        elif expected_type == "explanatory":
            assert any(s.name == "ABDUCTIVE" for s in strategies)
        elif expected_type == "creative":
            assert any(s.name == "LATERAL" for s in strategies)
        elif expected_type == "logical":
            assert any(s.name == "LOGICAL" for s in strategies)

@pytest.mark.asyncio
async def test_confidence_thresholds(
    orchestrator: ReasoningOrchestrator,
    sample_test_questions: List[Dict[str, Any]]
):
    """Test confidence thresholds for different question types"""
    for test_case in sample_test_questions:
        result = await orchestrator.reason(test_case["question"])
        assert result["confidence"] >= test_case["min_confidence"]

@pytest.mark.asyncio
async def test_source_requirements(
    orchestrator: ReasoningOrchestrator,
    sample_test_questions: List[Dict[str, Any]]
):
    """Test source requirements for different questions"""
    for test_case in sample_test_questions:
        result = await orchestrator.reason(test_case["question"])
        sources = result.get("metadata", {}).get("sources", [])
        assert len(sources) >= test_case["required_sources"]

@pytest.mark.asyncio
async def test_parallel_execution(orchestrator: ReasoningOrchestrator):
    """Test parallel execution of strategies"""
    # Use a question that should trigger multiple strategies
    question = "What causes climate change and how can we address it?"
    
    result = await orchestrator.reason(question)
    
    metadata = result.get("metadata", {})
    assert len(metadata.get("strategies_used", [])) > 1
    assert metadata.get("parallel_execution_time") is not None

@pytest.mark.asyncio
async def test_error_recovery(orchestrator: ReasoningOrchestrator):
    """Test recovery from strategy failures"""
    # Force a strategy to fail
    original_execute = orchestrator._execute_single_strategy
    failed_strategies = set()
    
    async def mock_execute(*args, **kwargs):
        strategy = args[1]
        if strategy not in failed_strategies:
            failed_strategies.add(strategy)
            raise Exception("Simulated failure")
        return await original_execute(*args, **kwargs)
    
    orchestrator._execute_single_strategy = mock_execute
    
    try:
        result = await orchestrator.reason("What is gravity?")
        assert result["confidence"] > 0
        assert "error_recovery" in result["metadata"]
    finally:
        orchestrator._execute_single_strategy = original_execute

@pytest.mark.asyncio
async def test_reasoning_steps_quality(
    orchestrator: ReasoningOrchestrator,
    sample_test_questions: List[Dict[str, Any]]
):
    """Test quality of reasoning steps"""
    for test_case in sample_test_questions:
        result = await orchestrator.reason(test_case["question"])
        steps = result.get("reasoning_steps", [])
        
        # Check step structure
        for step in steps:
            assert "step" in step
            assert "output" in step
            assert "confidence" in step
            
            # Check step content
            assert len(step["output"]) > 10  # Minimum content length
            assert 0 <= step["confidence"] <= 1
            
            # Check for evidence if required
            if test_case["required_sources"] > 0:
                assert "evidence" in step

@pytest.mark.asyncio
async def test_context_handling(orchestrator: ReasoningOrchestrator):
    """Test handling of context in reasoning"""
    context = {
        "previous_answers": [
            "Gravity is a fundamental force.",
            "Einstein described gravity in general relativity."
        ],
        "domain": "physics",
        "confidence_threshold": 0.8
    }
    
    result = await orchestrator.reason(
        "How does gravity affect time?",
        context=context
    )
    
    # Check context influence
    assert "general relativity" in result["answer"].lower()
    assert result["confidence"] >= context["confidence_threshold"]
    assert "context_used" in result["metadata"]

@pytest.mark.asyncio
async def test_invalid_inputs(orchestrator: ReasoningOrchestrator):
    """Test handling of invalid inputs"""
    # Empty question
    with pytest.raises(McpError):
        await orchestrator.reason("")
    
    # Too short
    with pytest.raises(McpError):
        await orchestrator.reason("Why?")
    
    # Invalid characters
    with pytest.raises(McpError):
        await orchestrator.reason("What is \x00 this?")

@pytest.mark.asyncio
async def test_cross_validation(
    orchestrator: ReasoningOrchestrator,
    validator,
    reviewer
):
    """Test cross-validation between components"""
    question = "What is photosynthesis?"
    
    # Get answer from orchestrator
    result = await orchestrator.reason(question)
    
    # Validate with basic validator
    validation = validator.validate(question, result["answer"])
    assert validation["valid"]
    
    # Review with advanced reviewer
    review = await reviewer.review(question, result["answer"])
    assert not review.needs_revision
    
    # Check confidence alignment
    assert abs(result["confidence"] - validation["confidence"]) < 0.2
    assert abs(result["confidence"] - review.overall_score) < 0.2

@pytest.mark.asyncio
async def test_performance_requirements(orchestrator: ReasoningOrchestrator):
    """Test performance requirements"""
    import time
    
    # Simple question should be fast
    start = time.time()
    await orchestrator.reason("What is 2+2?")
    simple_time = time.time() - start
    assert simple_time < 2  # Max 2 seconds
    
    # Complex question can take longer
    start = time.time()
    await orchestrator.reason(
        "What are the implications of quantum mechanics on our understanding of reality?"
    )
    complex_time = time.time() - start
    assert complex_time < 10  # Max 10 seconds
    
    # Parallel execution should be efficient
    start = time.time()
    await asyncio.gather(*[
        orchestrator.reason(q["question"])
        for q in sample_test_questions
    ])
    parallel_time = time.time() - start
    assert parallel_time < 15  # Max 15 seconds

@pytest.mark.asyncio
async def test_memory_management(orchestrator: ReasoningOrchestrator):
    """Test memory management during reasoning"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Run multiple complex queries
    for _ in range(5):
        await orchestrator.reason(
            "Explain the relationship between quantum mechanics and gravity."
        )
    
    final_memory = process.memory_info().rss
    memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
    
    assert memory_increase < 100  # Max 100MB increase