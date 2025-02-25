# Adaptive MCP Server Testing Guide

This document outlines the comprehensive testing strategy for the Adaptive MCP Server, providing developers with clear guidelines for test implementation, execution, and validation.

## Testing Philosophy

The Adaptive MCP Server follows a multi-layered testing approach to ensure robustness, reliability, and correctness:

1. **Unit Testing**: Verify the behavior of individual functions and components
2. **Integration Testing**: Verify the interaction between multiple components
3. **End-to-End Testing**: Verify the complete system behavior
4. **Performance Testing**: Verify system performance under load
5. **Error Handling Testing**: Verify graceful handling of errors

Our testing principles:
- **Test-driven development**: Write tests before implementation when possible
- **High coverage**: Maintain >90% code coverage for critical components
- **Realistic scenarios**: Test with real-world queries and research tasks
- **Comprehensive validation**: Test both success paths and error conditions

## Test Organization

Tests are organized in the `tests/` directory with the following structure:

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_reasoning/      # Tests for reasoning modules
│   ├── test_research/       # Tests for research modules
│   └── test_validators/     # Tests for validation modules
├── integration/             # Integration tests
│   ├── test_orchestrator.py # Tests for orchestrator
│   └── test_pipeline.py     # Tests for complete pipeline
├── e2e/                     # End-to-end tests
│   └── test_scenarios.py    # Real-world scenarios
└── performance/             # Performance tests
    └── test_benchmarks.py   # Benchmark tests
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_orchestrator.py

# Run tests matching a pattern
pytest -k "research"
```

### Coverage Testing

```bash
# Run with coverage
pytest --cov=.

# Generate HTML coverage report
pytest --cov=. --cov-report=html
```

### Parallel Testing

```bash
# Run tests in parallel
pytest -xvs -n auto
```

### Performance Testing

```bash
# Run benchmarks
pytest tests/performance/test_benchmarks.py --benchmark-only

# Compare against previous benchmarks
pytest-benchmark compare
```

## Writing Effective Tests

### Unit Test Example

```python
# test_sequential.py
import pytest
from unittest.mock import AsyncMock, patch
from reasoning.sequential import SequentialReasoner

@pytest.mark.asyncio
async def test_sequential_reasoning_basic():
    """Test basic sequential reasoning functionality"""
    reasoner = SequentialReasoner()
    
    # Mock research component
    with patch("research.exa_integration.search_information", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = "Test research results"
        
        # Execute reasoning
        result = await reasoner.reason("What is quantum computing?")
        
        # Assertions
        assert "answer" in result
        assert "confidence" in result
        assert result["confidence"] > 0
        assert len(result["reasoning_steps"]) > 0
        assert mock_search.called
```

### Integration Test Example

```python
# test_orchestrator.py
import pytest
from reasoning.orchestrator import reasoning_orchestrator, ReasoningStrategy

@pytest.mark.asyncio
async def test_orchestrator_strategy_selection():
    """Test strategy selection based on question type"""
    questions = {
        "What is quantum computing?": [ReasoningStrategy.SEQUENTIAL],
        "Why does gravity exist?": [ReasoningStrategy.ABDUCTIVE],
        "Create an innovative solution to climate change": [ReasoningStrategy.LATERAL],
        "If all humans are mortal and Socrates is human, what can we conclude?": [ReasoningStrategy.LOGICAL]
    }
    
    for question, expected_strategies in questions.items():
        # Test private method directly
        selected = reasoning_orchestrator._select_strategies(question)
        assert any(strategy in selected for strategy in expected_strategies)
```

### End-to-End Test Example

```python
# test_scenarios.py
import pytest
from mcp_client import AdaptiveMcpClient

@pytest.mark.asyncio
async def test_complex_question_scenario():
    """Test end-to-end handling of a complex question"""
    client = AdaptiveMcpClient("http://localhost:8000")
    response = await client.reason("Explain the potential long-term impacts of quantum computing on cryptography")
    
    # Verify response format
    assert "answer" in response
    assert "confidence" in response
    assert "reasoning_steps" in response
    
    # Verify quality criteria
    assert len(response["answer"]) > 100  # Sufficiently detailed
    assert response["confidence"] > 0.7   # High confidence
    assert len(response["reasoning_steps"]) >= 3  # Multiple reasoning steps
    
    # Verify content expectations
    answer = response["answer"].lower()
    assert "quantum" in answer
    assert "cryptography" in answer
    assert any(term in answer for term in ["encryption", "security", "algorithm"])
```

## Mocking External Dependencies

External dependencies should be mocked to ensure tests are isolated, predictable, and fast:

```python
@pytest.fixture
def mock_exa_search():
    """Fixture to mock Exa search responses"""
    with patch("research.exa_integration.ExaSearchIntegration.search") as mock:
        mock.return_value = [
            SearchResult(
                url="https://example.com/article",
                title="Test Article",
                text="This is test content about the search query.",
                relevance_score=0.95,
                source="example.com"
            )
        ]
        yield mock
```

## Test Data Management

Test data is managed through fixtures and test resources:

1. **Fixtures**: Pytest fixtures in `conftest.py` provide reusable test components
2. **Test Resources**: Static test data in `tests/resources/`

```python
@pytest.fixture
def sample_questions():
    """Sample questions for testing"""
    return [
        "What is quantum computing?",
        "Explain the theory of relativity",
        "How do neural networks function?",
        "What causes climate change?",
        "Describe the process of photosynthesis"
    ]
```

## Error Scenario Testing

Test error scenarios to ensure graceful handling:

```python
@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Test handling of various error scenarios"""
    # Test invalid input
    with pytest.raises(ValueError):
        await reasoning_orchestrator.reason("")
    
    # Test timeout handling
    with patch("research.exa_integration.ExaSearchIntegration.search", 
               side_effect=asyncio.TimeoutError("Search timed out")):
        result = await reasoning_orchestrator.reason("What is quantum computing?")
        assert result["confidence"] < 0.5  # Lower confidence due to search failure
        assert "answer" in result  # Still provides best-effort answer
```

## Performance Benchmarks

Performance benchmarks ensure the system meets performance standards:

```python
def test_reasoning_performance(benchmark):
    """Benchmark reasoning performance"""
    async def _run():
        return await reasoning_orchestrator.reason("What is quantum computing?")
    
    result = benchmark(lambda: asyncio.run(_run()))
    assert result["answer"]
```

## Continuous Integration

Tests are automatically run in CI for all pull requests and merges to main branches:

```yaml
# Example GitHub Actions workflow
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install -r requirements.txt
          python -m pip install -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=.
```

## Test Quality Guidelines

- **Descriptive Names**: Use descriptive test names that explain what is being tested
- **Arrange-Act-Assert**: Structure tests with clear setup, action, and verification phases
- **Isolated Tests**: Each test should be independent of other tests
- **Minimal Fixtures**: Keep test fixtures as simple as possible
- **Test Edge Cases**: Include tests for boundary conditions and edge cases
- **Readable Assertions**: Use clear, specific assertions
- **Helpful Error Messages**: Include meaningful error messages in assertions
- **Avoid Test Logic**: Minimize conditional logic in tests
- **Single Responsibility**: Each test should verify one specific behavior

## Troubleshooting Tests

Common test issues and solutions:

1. **Flaky Tests**: Tests that sometimes pass and sometimes fail
   - Check for race conditions or dependency on external state
   - Add explicit waits or timeouts
   - Increase test isolation

2. **Slow Tests**: 
   - Use profiling to identify bottlenecks
   - Mock external dependencies
   - Run tests in parallel

3. **Test Dependencies**:
   - Ensure test fixtures are properly set up and torn down
   - Use fresh fixtures for each test
   - Check for state leakage between tests

## Advanced Testing Topics

### Property-Based Testing

For certain components, property-based testing with Hypothesis can identify edge cases:

```python
import hypothesis
from hypothesis import strategies as st

@hypothesis.given(
    question=st.text(min_size=1, max_size=1000),
    confidence=st.floats(min_value=0, max_value=1)
)
def test_validator_properties(question, confidence):
    """Test validator properties across a range of inputs"""
    validator = AnswerValidator()
    result = validator.validate(question, f"The answer to '{question}'", {"confidence": confidence})
    
    # Properties that should always hold
    assert 0 <= result.confidence <= 1
    assert isinstance(result.valid, bool)
    assert all(0 <= score <= 1 for score in result.criteria_scores.values())
```

### Mutation Testing

Mutation testing helps identify weak spots in test coverage:

```bash
# Run mutation testing
mutmut run
```

### Load Testing

For API endpoints, load testing helps identify performance bottlenecks:

```bash
# Run locust load tests
locust -f tests/load/locustfile.py
```

## Conclusion

Thorough testing is essential for maintaining a robust, reliable Adaptive MCP Server. The investment in testing pays off through reduced bugs, easier maintenance, and more confident development.

Remember, tests are documentation. Well-written tests serve as examples of how your code should be used and what behavior should be expected.
