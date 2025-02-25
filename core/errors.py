"""
Custom Error Handling for Adaptive MCP Server
"""

class McpBaseError(Exception):
    """Base exception for all MCP server errors"""
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context or {}

class SearchError(McpBaseError):
    """Raised when search-related operations fail"""
    def __init__(self, message, search_query=None, **kwargs):
        super().__init__(message, context={
            'search_query': search_query,
            **kwargs
        })

class ResearchError(McpBaseError):
    """Raised when research operations encounter issues"""
    def __init__(self, message, research_context=None, **kwargs):
        super().__init__(message, context={
            'research_context': research_context,
            **kwargs
        })

class ReasoningError(McpBaseError):
    """Raised when reasoning modules encounter problems"""
    def __init__(self, message, reasoning_strategy=None, **kwargs):
        super().__init__(message, context={
            'reasoning_strategy': reasoning_strategy,
            **kwargs
        })

class ValidationError(McpBaseError):
    """Raised when validation checks fail"""
    def __init__(self, message, validation_details=None, **kwargs):
        super().__init__(message, context={
            'validation_details': validation_details,
            **kwargs
        })

class IntegrationError(McpBaseError):
    """Raised when module integration fails"""
    def __init__(self, message, modules_involved=None, **kwargs):
        super().__init__(message, context={
            'modules_involved': modules_involved,
            **kwargs
        })
