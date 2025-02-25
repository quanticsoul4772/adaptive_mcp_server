"""Tests for branching and abductive reasoning modules"""

import pytest
from ..reasoning.branching import BranchingReasoner, BranchingPath, BranchResult
from ..reasoning.abductive import AbductiveReasoner, Hypothesis

# Branching Reasoner Tests
@pytest.mark.asyncio
async def test_branching_initialization():
    """Test branching reasoner initialization"""
    reasoner = BranchingReasoner()
    assert len(reasoner.paths) == 3
    assert sum(p.weight for p in reasoner.paths) > 0

@pytest.mark.asyncio
async def test_branching_path_execution():
    """Test execution of individual reasoning paths"""
    reasoner = BranchingReasoner()
    question = "What is the capital of France?"
    
    # Test factual path
    result = await reasoner._factual_reasoning(question, None)
    assert "answer" in result
    assert "confidence" in result
    assert "reasoning_steps" in result
    
    # Test analytical path
    result = await reasoner._analytical_reasoning(question, None)
    assert len(result["reasoning_steps"]) >= 2
    assert "key_terms" in result["metadata"]
    
    # Test comparative path
    result = await reasoner._comparative_reasoning(question, None)
    assert "original_question" in result["metadata"]
    assert result["confidence"] <= 1.0

@pytest.mark.asyncio
async def test_branching_full_reasoning():
    """Test complete branching reasoning process"""
    reasoner = BranchingReasoner()
    result = await reasoner.reason("What is the capital of France?")
    
    assert "answer" in result
    assert "confidence" in result
    assert "selected_path" in result["metadata"]
    assert "attempted_paths" in result["metadata"]
    assert result["metadata"]["successful_paths"] > 0

# Abductive Reasoner Tests
@pytest.mark.asyncio
async def test_abductive_initialization():
    """Test abductive reasoner initialization"""
    reasoner = AbductiveReasoner(max_hypotheses=3)
    assert reasoner.max_hypotheses == 3
    assert len(reasoner.hypotheses) == 0

@pytest.mark.asyncio
async def test_hypothesis_generation():
    """Test generation of initial hypotheses"""
    reasoner = AbductiveReasoner()
    hypotheses = await reasoner._generate_hypotheses("What causes gravity?")
    
    assert len(hypotheses) <= reasoner.max_hypotheses
    assert all(isinstance(h, Hypothesis) for h in hypotheses)
    assert all(0 <= h.confidence <= 1 for h in hypotheses)

@pytest.mark.asyncio
async def test_evidence_gathering():
    """Test evidence gathering for hypotheses"""
    reasoner = AbductiveReasoner()
    supporting, counter = await reasoner._gather_evidence(
        "Gravity is caused by mass"
    )
    
    assert isinstance(supporting, list)
    assert isinstance(counter, list)
    assert all(isinstance(s, str) for s in supporting)
    assert all(isinstance(s, str) for s in counter)

def test_evidence_evaluation():
    """Test evidence quality evaluation"""
    reasoner = AbductiveReasoner()
    
    # Test with no evidence
    score = reasoner._evaluate_evidence([], [])
    assert score == 0.5
    
    # Test with only supporting evidence
    score = reasoner._evaluate_evidence(["strong evidence"], [])
    assert score > 0.5
    
    # Test with mixed evidence
    score = reasoner._evaluate_evidence(
        ["support 1", "support 2"],
        ["counter 1"]
    )
    assert 0 <= score <= 1

@pytest.mark.asyncio
async def test_abductive_full_reasoning():
    """Test complete abductive reasoning process"""
    reasoner = AbductiveReasoner()
    result = await reasoner.reason("What causes gravity?")
    
    assert "answer" in result
    assert "confidence" in result
    assert len(result["reasoning_steps"]) >= 3
    assert "evidence_summary" in result["metadata"]
    assert "validation" in result["metadata"]

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in both reasoners"""
    branching = BranchingReasoner()
    abductive = AbductiveReasoner()
    
    # Test with empty question
    with pytest.raises(Exception):
        await branching.reason("")
        
    with pytest.raises(Exception):
        await abductive.reason("")
