"""Tests for resource template handling"""

import pytest
from ..core.resources import ResourceTemplate, ResourceHandler
from ..core.errors import InvalidInputError, ResourceNotFoundError, ProcessingError

@pytest.fixture
def simple_template():
    """Create simple resource template"""
    return ResourceTemplate(
        template="users/{user_id}/profile",
        variables={"user_id": "string"},
        constraints={
            "user_id": {
                "type": "string",
                "pattern": r"[a-zA-Z0-9]+"
            }
        },
        description="User profile resource"
    )

@pytest.fixture
def complex_template():
    """Create complex resource template"""
    return ResourceTemplate(
        template="api/{version}/items/{item_id}/details/{format}",
        variables={
            "version": "string",
            "item_id": "integer",
            "format": "string"
        },
        constraints={
            "version": {
                "enum": ["v1", "v2", "v3"]
            },
            "item_id": {
                "type": "integer",
                "min": 1
            },
            "format": {
                "enum": ["json", "xml"]
            }
        },
        description="Item details resource"
    )

def test_template_compilation(simple_template):
    """Test template pattern compilation"""
    assert simple_template.pattern is not None
    
    # Test valid match
    match = simple_template.pattern.match("users/123/profile")
    assert match is not None
    assert match.group("user_id") == "123"
    
    # Test invalid match
    assert simple_template.pattern.match("users/profile") is None

def test_constraint_validation(complex_template):
    """Test constraint validation"""
    # Test valid values
    variables = complex_template.match("api/v1/items/123/details/json")
    assert variables is not None
    assert variables["version"] == "v1"
    assert variables["item_id"] == "123"
    assert variables["format"] == "json"
    
    # Test invalid version
    with pytest.raises(InvalidInputError):
        complex_template.match("api/v4/items/123/details/json")
    
    # Test invalid item_id
    with pytest.raises(InvalidInputError):
        complex_template.match("api/v1/items/0/details/json")
    
    # Test invalid format
    with pytest.raises(InvalidInputError):
        complex_template.match("api/v1/items/123/details/yaml")

def test_type_constraints():
    """Test type constraint handling"""
    template = ResourceTemplate(
        template="data/{id}/{value}/{flag}",
        variables={
            "id": "integer",
            "value": "number",
            "flag": "boolean"
        },
        constraints={
            "id": {"type": "integer"},
            "value": {"type": "number"},
            "flag": {"type": "boolean"}
        }
    )
    
    # Test valid values
    variables = template.match("data/123/45.67/true")
    assert variables is not None
    assert variables["id"] == "123"
    assert variables["value"] == "45.67"
    assert variables["flag"] == "true"
    
    # Test invalid integer
    with pytest.raises(InvalidInputError):
        template.match("data/12.3/45.67/true")
    
    # Test invalid number
    with pytest.raises(InvalidInputError):
        template.match("data/123/not-number/true")
    
    # Test invalid boolean
    with pytest.raises(InvalidInputError):
        template.match("data/123/45.67/maybe")

def test_format_constraints():
    """Test format constraint handling"""
    template = ResourceTemplate(
        template="events/{date}/{time}/{email}",
        variables={
            "date": "string",
            "time": "string",
            "email": "string"
        },
        constraints={
            "date": {"format": "date"},
            "time": {"format": "time"},
            "email": {"format": "email"}
        }
    )
    
    # Test valid values
    variables = template.match(
        "events/2024-02-23/14:30:00/test@example.com"
    )
    assert variables is not None
    
    # Test invalid date
    with pytest.raises(InvalidInputError):
        template.match(
            "events/2024-13-45/14:30:00/test@example.com"
        )
    
    # Test invalid time
    with pytest.raises(InvalidInputError):
        template.match(
            "events/2024-02-23/25:00:00/test@example.com"
        )
    
    # Test invalid email
    with pytest.raises(InvalidInputError):
        template.match(
            "events/2024-02-23/14:30:00/invalid-email"
        )

@pytest.mark.asyncio
async def test_resource_handler():
    """Test resource handler functionality"""
    handler = ResourceHandler()
    
    # Register handlers
    async def get_user(user_id: str):
        return {"id": user_id, "name": "Test User"}
    
    async def get_item(version: str, item_id: str, format: str):
        return {
            "version": version,
            "item_id": item_id,
            "format": format,
            "data": "Test Item"
        }
    
    handler.register(
        "users/{user_id}",
        {"user_id": "string"},
        get_user,
        {"user_id": {"type": "string"}}
    )
    
    handler.register(
        "api/{version}/items/{item_id}.{format}",
        {
            "version": "string",
            "item_id": "string",
            "format": "string"
        },
        get_item,
        {
            "version": {"enum": ["v1", "v2"]},
            "format": {"enum": ["json", "xml"]}
        }
    )
    
    # Test valid requests
    user_result = await handler.handle("users/123")
    assert user_result["id"] == "123"
    
    item_result = await handler.handle("api/v1/items/456.json")
    assert item_result["version"] == "v1"
    assert item_result["item_id"] == "456"
    
    # Test invalid requests
    with pytest.raises(ResourceNotFoundError):
        await handler.handle("invalid/path")
    
    with pytest.raises(InvalidInputError):
        await handler.handle("api/v3/items/456.json")  # Invalid version
    
    with pytest.raises(InvalidInputError):
        await handler.handle("api/v1/items/456.yaml")  # Invalid format

@pytest.mark.asyncio
async def test_handler_error_handling():
    """Test handler error handling"""
    handler = ResourceHandler()
    
    # Register handler that raises an error
    async def failing_handler(id: str):
        raise ValueError("Simulated error")
    
    handler.register(
        "test/{id}",
        {"id": "string"},
        failing_handler
    )
    
    # Test error handling
    with pytest.raises(ProcessingError) as exc_info:
        await handler.handle("test/123")
    assert "Simulated error" in str(exc_info.value)
    assert exc_info.value.details["uri"] == "test/123"

def test_resource_listing():
    """Test resource template listing"""
    handler = ResourceHandler()
    
    # Register multiple templates
    handler.register(
        "users/{user_id}",
        {"user_id": "string"},
        lambda x: x,
        description="User resource"
    )
    
    handler.register(
        "items/{item_id}",
        {"item_id": "string"},
        lambda x: x,
        description="Item resource"
    )
    
    # Test listing
    resources = handler.list_resources()
    assert len(resources) == 2
    assert any(r["description"] == "User resource" for r in resources)
    assert any(r["description"] == "Item resource" for r in resources)

def test_template_serialization(complex_template):
    """Test template serialization"""
    template_dict = complex_template.to_dict()
    
    assert template_dict["template"] == complex_template.template
    assert template_dict["variables"] == complex_template.variables
    assert template_dict["constraints"] == complex_template.constraints
    assert template_dict["description"] == complex_template.description

def test_resource_management():
    """Test resource registration and unregistration"""
    handler = ResourceHandler()
    
    # Register template
    handler.register(
        "test/{id}",
        {"id": "string"},
        lambda x: x,
        description="Test resource"
    )
    
    # Verify registration
    template = handler.get_template("test/{id}")
    assert template is not None
    assert template.description == "Test resource"
    
    # Unregister template
    handler.unregister("test/{id}")
    assert handler.get_template("test/{id}") is None
    assert len(handler.list_resources()) == 0

def test_concurrent_templates():
    """Test handling of multiple matching templates"""
    handler = ResourceHandler()
    
    # Register overlapping templates
    handler.register(
        "items/{id}",
        {"id": "string"},
        lambda x: "generic",
        description="Generic item"
    )
    
    handler.register(
        "items/{id}.{format}",
        {"id": "string", "format": "string"},
        lambda x, y: "formatted",
        description="Formatted item"
    )
    
    # Test matching
    assert handler.get_template("items/{id}") is not None
    assert handler.get_template("items/{id}.{format}") is not None
    
    # Ensure correct template is matched
    variables1 = handler.get_template("items/{id}").match("items/123")
    assert variables1 is not None
    assert "format" not in variables1
    
    variables2 = handler.get_template("items/{id}.{format}").match("items/123.json")
    assert variables2 is not None
    assert "format" in variables2