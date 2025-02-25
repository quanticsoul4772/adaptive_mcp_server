"""
Mock MCP types for testing
"""

class McpError(Exception):
    """Base class for all MCP errors"""
    pass

class ResourceNotFoundError(McpError):
    """Resource not found error"""
    pass
