# Testing Guide for Adaptive MCP Server

This document provides instructions for running tests in the Adaptive MCP Server project with or without external dependencies.

## Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install the package and test dependencies
pip install -e .
pip install pytest pytest-asyncio pytest-cov
```

## Running Tests with Mock Implementations

The project includes mock implementations for external dependencies. This allows tests to run without installing all dependencies:

```bash
# Run the simplified tests that use mock implementations
python -m pytest tests\test_simplified.py -v
```

These tests exercise the core functionality using mock implementations of:
- Research modules (nltk, transformers, aiohttp)
- Validation modules
- Reasoning modules 

## Running Tests with Full Dependencies

For complete testing with actual implementations, install all required dependencies:

```bash
# Install all dependencies
pip install -r requirements.txt

# Run all tests
python -m pytest
```

## Handling Missing Dependencies

The project is designed to gracefully handle missing dependencies by:
1. Using try/except blocks around import statements
2. Providing fallback implementations when dependencies are not available
3. Using mock modules for testing

### Key Mock Files:
- `research/mock.py`: Mock research implementation
- `validators/mock.py`: Mock validation implementation
- `reasoning/mock.py`: Mock reasoning implementation

## Running Specific Test Sets

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_simplified.py

# Run a specific test
python -m pytest tests/test_simplified.py::test_reasoning_basic

# Run with coverage report
python -m pytest --cov=.
```

## Adding New Tests

When adding new tests, follow these guidelines:

1. Use the async/await pattern for tests that call async functions
2. Always use `pytest.mark.asyncio` decorator for async tests
3. Use descriptive test names
4. Include both positive and negative test cases
5. Test error handling
6. Use mock implementations for external dependencies

Example:

```python
import pytest

@pytest.mark.asyncio
async def test_new_feature():
    """Description of what the test verifies"""
    # Test setup
    ...
    
    # Execute code being tested
    result = await feature_function()
    
    # Verify results
    assert result["expected_key"] == expected_value
```

## Continuous Integration

When setting up continuous integration:

1. Use the `-p no:conftest` option to skip the conftest.py file if it causes dependency issues
2. Run the simplified tests first, then full tests if dependencies are available
3. Configure test environments to handle missing dependencies gracefully

```bash
# Example CI testing command
python -m pytest tests/test_simplified.py -v
```

## Troubleshooting

If you encounter issues with tests:

1. **Missing dependencies**: Use the mock implementations
2. **Import errors**: Check that all mock implementations are properly set up
3. **API key issues**: The mock implementation provides a fallback "mock_api_key_for_testing"
4. **Test failures**: Check the test requirements and ensure the mocks match the expected interface

For any other issues, please create a GitHub issue with the details of the problem.
