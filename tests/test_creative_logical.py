"""Tests for lateral and logical reasoning modules"""

import pytest
from ..reasoning.lateral import LateralReasoner, CreativeApproach, CreativeResult
from ..reasoning.logical import LogicalReasoner, LogicalStatement, LogicalArgument, LogicOperator

# Lateral Reasoning Tests
@pytest.mark.asyncio
async def test_lateral_initialization():
    """Test lateral reasoner initialization"""
    reasoner = LateralReasoner()
    assert len(reasoner.approaches) == 3
    assert all(isinstance(a, CreativeApproach) for a in reasoner.approaches)

@pytest.mark.asyncio
async def test_analogical_thinking():
    """Test analogical thinking approach"""
    reasoner = LateralReasoner()
    result = await reasoner._analogical_thinking(
        "How to improve team communication?",
        None
    )
    
    assert isinstance(result, CreativeResult)
    assert 0 <= result.originality_score <= 1
    assert 0 <= result.usefulness_score <= 1
    assert len(result.reasoning_path) > 0

@pytest.mark.asyncio
async def test_random_association():
    """Test random association approach"""
    reasoner = LateralReasoner()
    result = await reasoner._random_association(
        "How to reduce energy consumption?",
        None
    )
    
    assert isinstance(result, CreativeResult)
    assert len(result.associations) > 0
    assert result.originality_score > 0.7  # Should be highly original

@pytest.mark.asyncio
async def test_perspective_shift():
    """Test perspective shifting approach"""
    reasoner = LateralReasoner()
    result = await reasoner._perspective_shift(
        "How to design a better product?",
        None
    )
    
    assert isinstance(result, CreativeResult)
    assert any("perspective" in step for step in result.reasoning_path)
    assert result.usefulness_score > 0.6  # Should be practical

@pytest.mark.asyncio
async def test_lateral_full_reasoning():
    """Test complete lateral reasoning process"""
    reasoner = LateralReasoner()
    result = await reasoner.reason("How to solve traffic congestion?")
    
    assert "answer" in result
    assert "confidence" in result
    assert "approach" in result["metadata"]
    assert "originality_score" in result["metadata"]

# Logical Reasoning Tests
@pytest.mark.asyncio
async def test_logical_initialization():
    """Test logical reasoner initialization"""
    reasoner = LogicalReasoner()
    assert len(reasoner.known_fallacies) > 0
    assert len(reasoner.statements) == 0

def test_logical_statement_detection():
    """Test identification of logical statements"""
    reasoner = LogicalReasoner()
    
    # Should be identified as logical statements
    assert reasoner._is_logical_statement("If it rains, then the ground is wet")
    assert reasoner._is_logical_statement("All humans must breathe oxygen")
    
    # Should not be identified as logical statements
    assert not reasoner._is_logical_statement("The sky is blue")
    assert not reasoner._is_logical_statement("I like pizza")

def test_statement_certainty():
    """Test certainty assessment of statements"""
    reasoner = LogicalReasoner()
    
    # Test certain statements
    certain = reasoner._assess_statement_certainty(
        "Definitely all squares have four sides"
    )
    assert certain > 0.7
    
    # Test uncertain statements
    uncertain = reasoner._assess_statement_certainty(
        "It might rain tomorrow"
    )
    assert uncertain < 0.5

def test_fallacy_detection():
    """Test detection of logical fallacies"""
    reasoner = LogicalReasoner()
    
    # Test circular reasoning
    conclusion = LogicalStatement("A is true", 1.0)
    premises = [LogicalStatement("A is true", 1.0)]
    assert reasoner._contains_fallacy(premises, conclusion)
    
    # Test hasty generalization
    conclusion = LogicalStatement("All birds can fly", 1.0)
    premises = [LogicalStatement("This bird can fly", 1.0)]
    assert reasoner._contains_fallacy(premises, conclusion)

@pytest.mark.asyncio
async def test_argument_construction():
    """Test logical argument construction"""
    reasoner = LogicalReasoner()
    
    premises = [
        LogicalStatement("All humans are mortal", 1.0),
        LogicalStatement("Socrates is human", 1.0)
    ]
    
    arguments = reasoner._construct_arguments(premises)
    assert len(arguments) > 0
    assert all(isinstance(a, LogicalArgument) for a in arguments)

@pytest.mark.asyncio
async def test_logical_full_reasoning():
    """Test complete logical reasoning process"""
    reasoner = LogicalReasoner()
    result = await reasoner.reason(
        "If all mammals are warm-blooded and dolphins are mammals, are dolphins warm-blooded?"
    )
    
    assert "answer" in result
    assert "confidence" in result
    assert "argument_structure" in result["metadata"]
    assert len(result["metadata"]["argument_structure"]["premises"]) > 0

def test_logical_connection_assessment():
    """Test assessment of logical connections"""
    reasoner = LogicalReasoner()
    
    # Strong logical connection
    strong_premises = [
        LogicalStatement("All A are B", 1.0),
        LogicalStatement("X is A", 1.0)
    ]
    strong_conclusion = LogicalStatement("Therefore X is B", 1.0)
    strong_score = reasoner._assess_logical_connection(strong_premises, strong_conclusion)
    assert strong_score > 0.7
    
    # Weak logical connection
    weak_premises = [
        LogicalStatement("Some A are B", 1.0)
    ]
    weak_conclusion = LogicalStatement("X might be B", 1.0)
    weak_score = reasoner._assess_logical_connection(weak_premises, weak_conclusion)
    assert weak_score < 0.5

def test_argument_validation():
    """Test complete argument validation"""
    reasoner = LogicalReasoner()
    
    # Valid argument
    valid_argument = LogicalArgument(
        premises=[
            LogicalStatement("All humans are mortal", 1.0),
            LogicalStatement("Socrates is human", 1.0)
        ],
        conclusion=LogicalStatement("Socrates is mortal", 1.0),
        validity_score=0.9,
        soundness_score=0.8
    )
    assert reasoner._validate_argument(valid_argument)
    
    # Invalid argument (low scores)
    invalid_argument = LogicalArgument(
        premises=[
            LogicalStatement("Some birds fly", 0.5)
        ],
        conclusion=LogicalStatement("All birds fly", 0.5),
        validity_score=0.4,
        soundness_score=0.3
    )
    assert not reasoner._validate_argument(invalid_argument)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in both reasoners"""
    lateral = LateralReasoner()
    logical = LogicalReasoner()
    
    # Test with empty input
    with pytest.raises(Exception):
        await lateral.reason("")
    
    with pytest.raises(Exception):
        await logical.reason("")
    
    # Test with invalid input
    with pytest.raises(Exception):
        await lateral.reason("   ")
    
    with pytest.raises(Exception):
        await logical.reason("   ")
