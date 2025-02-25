"""
Comprehensive Tests for Reasoning Strategies Integration

These tests validate the integration and cooperation between different reasoning strategies.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import logging
from typing import Dict, Any, List

# Import reasoning components
from reasoning.orchestrator import reasoning_orchestrator, ReasoningStrategy, StrategyResult
from reasoning.sequential import SequentialReasoner
from reasoning.branching import BranchingReasoner
from reasoning.abductive import AbductiveReasoner
from reasoning.lateral import LateralReasoner
from reasoning.logical import LogicalReasoner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test.reasoning_strategies")

# Test questions categorized by most appropriate reasoning strategy
TEST_QUESTIONS = {
    ReasoningStrategy.SEQUENTIAL: [
        "What is quantum computing?",
        "Explain how photosynthesis works",
        "What is the capital of France?"
    ],
    ReasoningStrategy.BRANCHING: [
        "Compare and contrast nuclear and solar energy",
        "What are the pros and cons of remote work?",
        "Evaluate different approaches to tackling climate change"
    ],
    ReasoningStrategy.ABDUCTIVE: [
        "Why do leaves change color in autumn?",
        "What caused the 2008 financial crisis?",
        "Why do some animals hibernate?"
    ],
    ReasoningStrategy.LATERAL: [
        "Imagine a world without internet",
        "Generate creative solutions for urban transportation",
        "How might we redesign education for the digital age?"
    ],
    ReasoningStrategy.LOGICAL: [
        "If all humans are mortal and Socrates is human, what can we conclude?",
        "In a valid syllogism, if premises are true, what can we say about the conclusion?",
        "Given that A implies B, and B implies C, what can we deduce about A and C?"
    ]
}

@pytest.fixture
def mock_research_context():
    """Create a mock research context for testing"""
    from research.research_integrator import ResearchContext
    from research.exa_integration import SearchResult
    
    return ResearchContext(
        original_query="test query",
        processed_queries=["test query"],
        search_results=[
            SearchResult(
                url="https://example.com/article",
                title="Test Article",
                text="This is test content about the query.",
                relevance_score=0.9,
                source="example.com"
            )
        ],
        confidence=0.85
    )

@pytest.mark.asyncio
@pytest.mark.parametrize("strategy,questions", TEST_QUESTIONS.items())
async def test_strategy_selection(strategy, questions):
    """Test strategy selection based on question characteristics"""
    for question in questions:
        # Use internal method to select strategies
        selected_strategies = reasoning_orchestrator._select_strategies(question)
        
        # Verify expected strategy is selected
        strategy_names = [s.name for s in selected_strategies]
        assert strategy.name in strategy_names, f"Expected {strategy.name} for question: {question}"

@pytest.fixture
def mock_reasoning_modules():
    """Mock all reasoning modules to return predictable results"""
    # Create mock results for each strategy
    mock_results = {
        ReasoningStrategy.SEQUENTIAL: StrategyResult(
            strategy=ReasoningStrategy.SEQUENTIAL,
            answer="Sequential reasoning answer",
            confidence=0.8,
            reasoning_steps=[{"step": "Sequential step", "output": "Sequential output"}]
        ),
        ReasoningStrategy.BRANCHING: StrategyResult(
            strategy=ReasoningStrategy.BRANCHING,
            answer="Branching reasoning answer",
            confidence=0.75,
            reasoning_steps=[{"step": "Branching step", "output": "Branching output"}]
        ),
        ReasoningStrategy.ABDUCTIVE: StrategyResult(
            strategy=ReasoningStrategy.ABDUCTIVE,
            answer="Abductive reasoning answer",
            confidence=0.7,
            reasoning_steps=[{"step": "Abductive step", "output": "Abductive output"}]
        ),
        ReasoningStrategy.LATERAL: StrategyResult(
            strategy=ReasoningStrategy.LATERAL,
            answer="Lateral reasoning answer",
            confidence=0.65,
            reasoning_steps=[{"step": "Lateral step", "output": "Lateral output"}]
        ),
        ReasoningStrategy.LOGICAL: StrategyResult(
            strategy=ReasoningStrategy.LOGICAL,
            answer="Logical reasoning answer",
            confidence=0.85,
            reasoning_steps=[{"step": "Logical step", "output": "Logical output"}]
        )
    }
    
    # Create patch for _execute_single_strategy
    with patch.object(reasoning_orchestrator, '_execute_single_strategy') as mock:
        async def side_effect(strategy, question, research_context=None):
            return mock_results[strategy]
        
        mock.side_effect = side_effect
        yield mock

@pytest.mark.asyncio
async def test_strategy_execution(mock_reasoning_modules, mock_research_context):
    """Test execution of multiple reasoning strategies"""
    # Execute reasoning with default strategy selection
    result = await reasoning_orchestrator.reason("Test multi-strategy question")
    
    # Verify strategies were executed
    assert mock_reasoning_modules.called
    
    # Verify result integration
    assert "answer" in result
    assert "confidence" in result
    assert "reasoning_steps" in result
    assert "metadata" in result
    
    # Check metadata for strategy info
    metadata = result.get("metadata", {})
    assert "strategies_used" in metadata or "selected_strategy" in metadata

@pytest.mark.asyncio
async def test_strategy_combination(mock_reasoning_modules):
    """Test combination of results from multiple strategies"""
    # Force execution of all strategies
    with patch.object(reasoning_orchestrator, '_select_strategies') as mock_select:
        mock_select.return_value = list(ReasoningStrategy)
        
        result = await reasoning_orchestrator.reason("Combine all strategies")
        
        # Verify multiple strategies were used
        assert mock_reasoning_modules.call_count == len(list(ReasoningStrategy))
        
        # Verify combined result
        assert "answer" in result
        assert "Based on multiple reasoning approaches" in result["answer"]
        
        # Verify all strategies contributed
        for strategy in ReasoningStrategy:
            assert strategy.name in result["answer"]

@pytest.mark.asyncio
async def test_confidence_based_selection():
    """Test selection of results based on confidence scores"""
    # Create mock strategy results with varying confidence
    high_confidence = StrategyResult(
        strategy=ReasoningStrategy.LOGICAL,
        answer="High confidence answer",
        confidence=0.9,
        reasoning_steps=[{"step": "Logical step", "output": "Logical output"}]
    )
    
    low_confidence = StrategyResult(
        strategy=ReasoningStrategy.LATERAL,
        answer="Low confidence answer",
        confidence=0.4,
        reasoning_steps=[{"step": "Lateral step", "output": "Lateral output"}]
    )
    
    # Mock validation to return original results
    with patch.object(reasoning_orchestrator, '_validate_results') as mock_validate:
        mock_validate.return_value = [high_confidence, low_confidence]
        
        # Mock execution to return our prepared results
        with patch.object(reasoning_orchestrator, '_execute_single_strategy') as mock_execute:
            async def side_effect(strategy, question, research_context=None):
                if strategy == ReasoningStrategy.LOGICAL:
                    return high_confidence
                else:
                    return low_confidence
            
            mock_execute.side_effect = side_effect
            
            # Mock strategy selection
            with patch.object(reasoning_orchestrator, '_select_strategies') as mock_select:
                mock_select.return_value = [ReasoningStrategy.LOGICAL, ReasoningStrategy.LATERAL]
                
                # Test reasoning
                result = await reasoning_orchestrator.reason("Test confidence selection")
                
                # Verify high confidence result prioritized
                assert result["confidence"] >= high_confidence.confidence
                assert high_confidence.answer in result["answer"]

@pytest.mark.asyncio
async def test_sequential_reasoning_steps():
    """Test sequential reasoning produces meaningful steps"""
    # Use actual SequentialReasoner for this test
    reasoner = SequentialReasoner()
    
    # Mock search integration
    with patch('reasoning.sequential.search_information', new_callable=AsyncMock) as mock_search:
        mock_search.return_value = "Test search results about quantum computing"
        
        # Execute reasoning
        result = await reasoner.reason("What is quantum computing?")
        
        # Verify structure
        assert "answer" in result
        assert "confidence" in result
        assert "reasoning_steps" in result
        
        # Verify steps content
        steps = result["reasoning_steps"]
        assert len(steps) >= 3, "Expected at least 3 steps in sequential reasoning"
        
        # Check for expected step types
        step_names = [step["step"] for step in steps]
        assert "Parse question" in step_names
        assert "Research" in step_names
        assert "Form answer" in step_names

@pytest.mark.asyncio
async def test_logical_strategy_for_deduction():
    """Test logical reasoning for deductive questions"""
    # Use actual LogicalReasoner
    reasoner = LogicalReasoner()
    
    # Execute reasoning with a syllogism
    syllogism = "If all birds have wings, and penguins are birds, what can we conclude about penguins?"
    result = await reasoner.reason(syllogism)
    
    # Verify structure and content
    assert "answer" in result
    assert "wings" in result["answer"].lower()
    assert "penguins" in result["answer"].lower()
    assert result["confidence"] > 0.7, "Expected high confidence for clear syllogism"

@pytest.mark.asyncio
async def test_branching_reasoning_paths():
    """Test branching reasoning explores multiple paths"""
    # Use actual BranchingReasoner
    reasoner = BranchingReasoner()
    
    # Execute reasoning
    result = await reasoner.reason("Compare wind and solar energy")
    
    # Verify multiple branches explored
    assert "answer" in result
    
    # Look for branch exploration in steps or answer
    branches_explored = False
    if "reasoning_steps" in result:
        steps = result["reasoning_steps"]
        branches_explored = any("branch" in str(step).lower() for step in steps)
    
    if not branches_explored:
        branches_explored = "branch" in result["answer"].lower()
    
    assert branches_explored, "Expected evidence of branch exploration"
    
    # Check for comparison elements
    answer = result["answer"].lower()
    assert "wind" in answer and "solar" in answer
    assert any(term in answer for term in ["advantage", "disadvantage", "compare", "contrast"])

@pytest.mark.asyncio
async def test_abductive_hypothesis_formation():
    """Test abductive reasoning forms and evaluates hypotheses"""
    # Use actual AbductiveReasoner
    reasoner = AbductiveReasoner()
    
    # Execute reasoning
    result = await reasoner.reason("Why do leaves change color in autumn?")
    
    # Verify hypothesis formation
    assert "answer" in result
    answer = result["answer"].lower()
    
    # Check for hypothesis language
    assert any(term in answer for term in ["hypothesis", "possible explanation", "reason", "because", "cause"])
    
    # Check for specific content about leaf color change
    assert "leaves" in answer
    assert "color" in answer
    assert "autumn" in answer or "fall" in answer

@pytest.mark.asyncio
async def test_lateral_creative_thinking():
    """Test lateral thinking produces creative outputs"""
    # Use actual LateralReasoner
    reasoner = LateralReasoner()
    
    # Execute reasoning
    result = await reasoner.reason("Propose an innovative solution to urban transportation")
    
    # Verify creative output
    assert "answer" in result
    answer = result["answer"].lower()
    
    # Check for creativity indicators
    assert any(term in answer for term in ["innovation", "creative", "novel", "unique", "alternative", "solution"])
    
    # Check for transportation content
    assert "transportation" in answer or "transport" in answer
    assert "urban" in answer or "city" in answer

@pytest.mark.asyncio
async def test_fallback_to_sequential():
    """Test fallback to sequential reasoning when other strategies fail"""
    # Mock all strategies to fail except sequential
    async def mock_execute(strategy, question, research_context=None):
        if strategy == ReasoningStrategy.SEQUENTIAL:
            return StrategyResult(
                strategy=ReasoningStrategy.SEQUENTIAL,
                answer="Sequential fallback answer",
                confidence=0.7,
                reasoning_steps=[{"step": "Sequential step", "output": "Sequential output"}]
            )
        else:
            # Simulate failure for other strategies
            return StrategyResult(
                strategy=strategy,
                answer="",
                confidence=0.0,
                reasoning_steps=[],
                metadata={"error": "Strategy failed"}
            )
    
    with patch.object(reasoning_orchestrator, '_execute_single_strategy', side_effect=mock_execute):
        # Force multiple strategy selection
        with patch.object(reasoning_orchestrator, '_select_strategies') as mock_select:
            mock_select.return_value = list(ReasoningStrategy)
            
            # Execute reasoning
            result = await reasoning_orchestrator.reason("Test fallback mechanism")
            
            # Verify sequential was used as fallback
            assert "answer" in result
            assert result["answer"] == "Sequential fallback answer"
            
            # Check metadata for fallback indication
            metadata = result.get("metadata", {})
            selected_strategy = metadata.get("selected_strategy", "")
            assert "SEQUENTIAL" in selected_strategy

@pytest.mark.asyncio
async def test_combined_confidence_calculation():
    """Test confidence calculation when combining multiple strategy results"""
    # Test with mock strategy results of different confidences
    strategy_results = [
        StrategyResult(
            strategy=ReasoningStrategy.LOGICAL,
            answer="Logical answer",
            confidence=0.9,
            reasoning_steps=[{"step": "Logical step", "output": "Logical output"}]
        ),
        StrategyResult(
            strategy=ReasoningStrategy.SEQUENTIAL,
            answer="Sequential answer",
            confidence=0.7,
            reasoning_steps=[{"step": "Sequential step", "output": "Sequential output"}]
        )
    ]
    
    # Access private method for testing
    combined_result = reasoning_orchestrator._combine_results(strategy_results)
    
    # Verify combined confidence calculation
    assert "confidence" in combined_result
    # Should be average of individual confidences
    expected_confidence = (0.9 + 0.7) / 2
    assert abs(combined_result["confidence"] - expected_confidence) < 0.01

@pytest.mark.asyncio
async def test_empty_results_handling():
    """Test handling of case where no strategies produce valid results"""
    # Mock to return empty valid results
    with patch.object(reasoning_orchestrator, '_validate_results') as mock_validate:
        mock_validate.return_value = []
        
        # Execute reasoning
        result = await reasoning_orchestrator.reason("Question that stumps all strategies")
        
        # Verify graceful handling
        assert "answer" in result
        assert "confidence" in result
        assert result["confidence"] == 0.0
        assert "Unable to generate" in result["answer"]

@pytest.mark.asyncio
async def test_reasoning_with_validation():
    """Test final validation step of reasoning results"""
    # Mock standard reasoning to produce a result
    mock_result = {
        "answer": "Test answer",
        "confidence": 0.8,
        "reasoning_steps": [{"step": "Test step", "output": "Test output"}],
        "metadata": {"strategy_used": "SEQUENTIAL"}
    }
    
    with patch.object(reasoning_orchestrator, '_combine_results') as mock_combine:
        mock_combine.return_value = mock_result
        
        # Mock validation to add validation results
        with patch('validators.advanced_validator.validate') as mock_validate:
            mock_validate.return_value = {
                "valid": True,
                "confidence": 0.85,
                "validation_details": {"semantic_score": 0.9, "factual_score": 0.8}
            }
            
            # Execute reasoning
            result = await reasoning_orchestrator.reason("Test validation integration")
            
            # Verify validation was applied
            assert "validation" in result
            assert result["validation"]["valid"]
            assert "validation_details" in result["validation"]
