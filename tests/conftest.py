"""
Global test configuration and fixtures.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from adaptive_mcp_server.reasoning.sequential import SequentialReasoner
from adaptive_mcp_server.reasoning.branching import BranchingReasoner
from adaptive_mcp_server.reasoning.abductive import AbductiveReasoner
from adaptive_mcp_server.reasoning.lateral import LateralReasoner
from adaptive_mcp_server.reasoning.logical import LogicalReasoner
from adaptive_mcp_server.reasoning.orchestrator import ReasoningOrchestrator
from adaptive_mcp_server.validators.basic_validator import AnswerValidator
from adaptive_mcp_server.validators.reviewer import AnswerReviewer
from adaptive_mcp_server.research.enhanced_search import EnhancedSearchManager

@pytest.fixture
def sample_question() -> str:
    """Sample question for testing"""
    return "What is the capital of France?"

@pytest.fixture
def sample_answer() -> str:
    """Sample answer for testing"""
    return "The capital of France is Paris. It has been the capital since 987 CE."

@pytest.fixture
def sample_reasoning_steps() -> List[Dict[str, Any]]:
    """Sample reasoning steps for testing"""
    return [
        {
            "step": "Initial research",
            "output": "Found multiple sources confirming Paris as capital",
            "confidence": 0.9,
            "evidence": ["Geographic database", "Historical records"]
        },
        {
            "step": "Verification",
            "output": "Cross-referenced with official sources",
            "confidence": 0.95,
            "evidence": ["Government records"]
        }
    ]

@pytest.fixture
def sample_metadata() -> Dict[str, Any]:
    """Sample metadata for testing"""
    return {
        "strategies_used": ["research", "verification"],
        "confidence": 0.92,
        "sources": ["Geographic database", "Government records"],
        "processing_time": 1.5
    }

@pytest.fixture
def sequential_reasoner() -> SequentialReasoner:
    """Sequential reasoner instance"""
    return SequentialReasoner()

@pytest.fixture
def branching_reasoner() -> BranchingReasoner:
    """Branching reasoner instance"""
    return BranchingReasoner()

@pytest.fixture
def abductive_reasoner() -> AbductiveReasoner:
    """Abductive reasoner instance"""
    return AbductiveReasoner()

@pytest.fixture
def lateral_reasoner() -> LateralReasoner:
    """Lateral reasoner instance"""
    return LateralReasoner()

@pytest.fixture
def logical_reasoner() -> LogicalReasoner:
    """Logical reasoner instance"""
    return LogicalReasoner()

@pytest.fixture
def orchestrator() -> ReasoningOrchestrator:
    """Orchestrator instance"""
    return ReasoningOrchestrator()

@pytest.fixture
def validator() -> AnswerValidator:
    """Answer validator instance"""
    return AnswerValidator()

@pytest.fixture
def reviewer() -> AnswerReviewer:
    """Answer reviewer instance"""
    return AnswerReviewer()

@pytest.fixture
def search_manager() -> EnhancedSearchManager:
    """Search manager instance"""
    return EnhancedSearchManager()

@pytest.fixture
def sample_test_questions() -> List[Dict[str, Any]]:
    """Set of test questions with expected results"""
    return [
        {
            "question": "What is the capital of France?",
            "expected_type": "factual",
            "min_confidence": 0.8,
            "required_sources": 2
        },
        {
            "question": "Why is the sky blue?",
            "expected_type": "explanatory",
            "min_confidence": 0.7,
            "required_sources": 1
        },
        {
            "question": "How can we reduce plastic waste?",
            "expected_type": "creative",
            "min_confidence": 0.6,
            "required_sources": 2
        },
        {
            "question": "If all humans are mortal, and Socrates is human, what can we conclude?",
            "expected_type": "logical",
            "min_confidence": 0.9,
            "required_sources": 1
        }
    ]

@pytest.fixture
def mock_search_results() -> List[Dict[str, Any]]:
    """Mock search results for testing"""
    return [
        {
            "content": "Paris is the capital of France since 987 CE.",
            "url": "https://example.com/history",
            "score": 0.95
        },
        {
            "content": "France's capital city Paris is home to 2.2 million people.",
            "url": "https://example.org/demographics",
            "score": 0.92
        }
    ]

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
