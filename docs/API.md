# Adaptive MCP Server API Documentation

## Overview

The Adaptive MCP Server provides a flexible reasoning system that combines multiple strategies with real-time research capabilities. This document outlines the available endpoints and their usage.

## Core Components

### 1. Reasoning Module

#### Available Strategies:
- **Sequential**: Linear step-by-step reasoning
- **Branching**: Parallel exploration of multiple paths
- **Abductive**: Hypothesis-based reasoning
- **Lateral**: Creative thinking approaches
- **Logical**: Formal logical deduction

#### Endpoint: `/reason`
```json
POST /reason
{
    "question": "string",
    "strategy": "string" (optional),
    "context": {} (optional)
}
```

Returns:
```json
{
    "answer": "string",
    "confidence": float,
    "reasoning_steps": [
        {
            "step": "string",
            "output": "string",
            "confidence": float
        }
    ],
    "metadata": {
        "strategy_used": "string",
        "processing_time": float,
        "sources": ["string"]
    }
}
```

### 2. Research Integration

The server integrates with multiple search providers:
- Exa Search API (primary)
- Brave Search API (fallback)

Features:
- Query refinement
- Source credibility assessment
- Result validation
- Multi-source corroboration

### 3. Validation System

Components:
- Basic Validator: Quick validation of answers
- AI Self-Review: Comprehensive review of reasoning
- Evidence Verification: Source checking

Review criteria:
- Completeness
- Relevance
- Accuracy
- Clarity
- Consistency

### 4. Explanation System

Formats:
- Markdown
- Plain text
- JSON

Components:
- Step-by-step reasoning
- Evidence linking
- Source citations
- Confidence scores

## Usage Examples

### Basic Query
```python
import requests

response = requests.post("http://localhost:8000/reason", json={
    "question": "What is quantum computing?"
})

print(response.json())
```

### Strategy Selection
```python
response = requests.post("http://localhost:8000/reason", json={
    "question": "What causes gravity?",
    "strategy": "abductive"
})
```

### Context Usage
```python
response = requests.post("http://localhost:8000/reason", json={
    "question": "Why is this happening?",
    "context": {
        "previous_answers": ["..."],
        "domain": "physics"
    }
})
```

## Error Handling

The server uses standard HTTP status codes:
- 200: Success
- 400: Invalid request
- 500: Server error

Error responses include:
```json
{
    "error": "string",
    "detail": "string",
    "suggestion": "string"
}
```

## Configuration

Server configuration can be customized via `mcp_config.json`:
```json
{
    "name": "adaptive-mcp-server",
    "version": "0.1.0",
    "capabilities": {
        "tools": {"listChanged": true},
        "resources": {
            "subscribe": true,
            "listChanged": true
        }
    }
}
```

## Best Practices

1. **Strategy Selection**:
   - Use sequential for straightforward questions
   - Use branching for complex problems
   - Use abductive for explanatory questions
   - Use lateral for creative problems
   - Use logical for deductive reasoning

2. **Context Usage**:
   - Always provide relevant context
   - Include domain information
   - Reference previous interactions

3. **Error Handling**:
   - Implement proper error handling
   - Provide fallback strategies
   - Handle timeouts appropriately

4. **Performance**:
   - Use appropriate timeouts
   - Implement rate limiting
   - Cache common queries