"""Tests for error handling module"""

import pytest
from ..core.errors import (
    ErrorType,
    ErrorResponse,
    McpError,
    InvalidInputError,
    ResourceNotFoundError,
    ValidationError,
    ProcessingError,
    TimeoutError,
    handle_error
)

def test_error_response_creation():
    """Test creation of error responses"""
    response = ErrorResponse(
        error=ErrorType.INVALID_INPUT,
        message="Invalid input provided",
        details={"field": "question"},
        suggestion="Please provide a valid question"
    )
    
    assert response.error == ErrorType.INVALID_INPUT
    assert "Invalid input" in response.message
    assert response.details["field"] == "question"
    assert "valid question" in response.suggestion

def test_error_response_to_dict():
    """Test conversion of error response to dictionary"""
    response = ErrorResponse(
        error=ErrorType.VALIDATION_FAILED,
        message="Validation failed",
        details={"score": 0.5}
    )
    
    dict_response = response.to_dict()
    assert dict_response["error"] == "VALIDATION_FAILED"
    assert dict_response["message"] == "Validation failed"
    assert dict_response["details"]["score"] == 0.5
    assert "suggestion" not in dict_response

def test_mcp_error_creation():
    """Test creation of MCP errors"""
    error = McpError(
        ErrorType.PROCESSING_ERROR,
        "Processing failed",
        {"step": "reasoning"},
        "Try simplifying the question"
    )
    
    assert error.error_type == ErrorType.PROCESSING_ERROR
    assert "Processing failed" in str(error)
    assert error.details["step"] == "reasoning"
    assert "simplifying" in error.suggestion

def test_specific_error_types():
    """Test specific error type creation"""
    # Test InvalidInputError
    input_error = InvalidInputError(
        "Invalid question format",
        {"field": "question", "value": ""},
        "Question cannot be empty"
    )
    assert input_error.error_type == ErrorType.INVALID_INPUT
    
    # Test ResourceNotFoundError
    resource_error = ResourceNotFoundError(
        "Source not found",
        {"source_id": "123"},
        "Check source ID and try again"
    )
    assert resource_error.error_type == ErrorType.RESOURCE_NOT_FOUND
    
    # Test ValidationError
    validation_error = ValidationError(
        "Answer validation failed",
        {"confidence": 0.3},
        "Try providing more detailed answer"
    )
    assert validation_error.error_type == ErrorType.VALIDATION_FAILED
    
    # Test ProcessingError
    process_error = ProcessingError(
        "Processing timeout",
        {"timeout": 30},
        "Try breaking down the request"
    )
    assert process_error.error_type == ErrorType.PROCESSING_ERROR

def test_error_conversion():
    """Test conversion of standard exceptions to MCP format"""
    # Test ValueError conversion
    value_error = ValueError("Invalid value")
    response = handle_error(value_error)
    assert response.error == ErrorType.INVALID_INPUT
    
    # Test TimeoutError conversion
    timeout_error = TimeoutError("Operation timed out")
    response = handle_error(timeout_error)
    assert response.error == ErrorType.TIMEOUT_ERROR
    
    # Test unknown error conversion
    unknown_error = Exception("Unknown error")
    response = handle_error(unknown_error)
    assert response.error == ErrorType.PROCESSING_ERROR
    assert "Unexpected error" in response.message

def test_error_response_in_handlers():
    """Test error handling in request handlers"""
    async def mock_handler():
        raise InvalidInputError(
            "Invalid question",
            {"field": "question", "value": ""},
            "Please provide a non-empty question"
        )
    
    @pytest.mark.asyncio
    async def test_handler():
        try:
            await mock_handler()
        except Exception as e:
            response = handle_error(e)
            assert response.error == ErrorType.INVALID_INPUT
            assert "Invalid question" in response.message
            assert response.details["field"] == "question"
            assert "non-empty" in response.suggestion

def test_error_chaining():
    """Test error chaining and preservation"""
    try:
        try:
            raise ValueError("Original error")
        except ValueError as e:
            raise ProcessingError(
                "Processing failed",
                {"original_error": str(e)},
                "Please try again"
            ) from e
    except Exception as e:
        response = handle_error(e)
        assert response.error == ErrorType.PROCESSING_ERROR
        assert "Original error" in response.details["original_error"]

def test_error_suggestion_generation():
    """Test automatic suggestion generation"""
    # Test input validation suggestions
    input_error = InvalidInputError("Question too long")
    response = handle_error(input_error)
    assert "try" in response.suggestion.lower()
    
    # Test timeout suggestions
    timeout_error = TimeoutError("Operation timed out")
    response = handle_error(timeout_error)
    assert "breaking down" in response.suggestion.lower()
    
    # Test processing error suggestions
    process_error = ProcessingError("Unknown processing error")
    response = handle_error(process_error)
    assert "contact support" in response.suggestion.lower()

def test_error_response_validation():
    """Test validation of error response format"""
    # Test required fields
    with pytest.raises(ValueError):
        ErrorResponse(
            error=None,  # type: ignore
            message="Test"
        )
    
    with pytest.raises(ValueError):
        ErrorResponse(
            error=ErrorType.INVALID_INPUT,
            message=""
        )
    
    # Test valid response
    response = ErrorResponse(
        error=ErrorType.INVALID_INPUT,
        message="Test message",
        details={"test": True}
    )
    dict_response = response.to_dict()
    assert all(k in dict_response for k in ["error", "message", "details"])

def test_custom_error_creation():
    """Test creation of custom error types"""
    class CustomError(McpError):
        def __init__(self, message: str):
            super().__init__(
                ErrorType.PROCESSING_ERROR,
                message,
                {"custom": True},
                "Custom suggestion"
            )
    
    error = CustomError("Custom error")
    response = handle_error(error)
    assert response.error == ErrorType.PROCESSING_ERROR
    assert response.details["custom"] is True
    assert "Custom suggestion" in response.suggestion

def test_batch_error_handling():
    """Test handling multiple errors"""
    errors = [
        ValueError("Invalid input"),
        ResourceNotFoundError("Resource not found"),
        TimeoutError("Operation timed out")
    ]
    
    responses = [handle_error(e) for e in errors]
    assert len(responses) == 3
    assert responses[0].error == ErrorType.INVALID_INPUT
    assert responses[1].error == ErrorType.RESOURCE_NOT_FOUND
    assert responses[2].error == ErrorType.TIMEOUT_ERROR