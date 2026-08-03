"""Pytest configuration and shared fixtures."""

import pytest


class MockParameter:
    """Mock tool parameter."""
    def __init__(self, name="param", param_type="str", default=None):
        self.name = name
        self.type = param_type
        self.default = default
        self.required = default is None


class MockSchema:
    """Mock tool schema."""
    def __init__(self, tool_id="tool1", category="text", return_type="str"):
        self.id = tool_id
        self.category = category
        self.return_type = return_type
        self.description = f"Mock tool: {tool_id}"
        self.capabilities = ["analysis", "reasoning"]
        self.parameters = [MockParameter("input", "str")]
        self.requires_network = False


class MockRegistry:
    """Mock tool registry."""
    def __init__(self, tool_schemas=None):
        """Initialize with optional predefined schemas."""
        self.schemas = tool_schemas or {}

    def get(self, tool_id):
        """Get tool schema by ID."""
        if tool_id in self.schemas:
            return (self.schemas[tool_id], None)

        # Generate default mock schema
        schema = MockSchema(tool_id=tool_id)
        return (schema, None)

    def list_all(self):
        """List all tools."""
        return list(self.schemas.keys())


@pytest.fixture
def mock_registry():
    """Create a mock tool registry for testing."""
    schemas = {
        "math.add": MockSchema("math.add", "math", "float"),
        "math.multiply": MockSchema("math.multiply", "math", "float"),
        "text.uppercase": MockSchema("text.uppercase", "text", "str"),
        "text.split": MockSchema("text.split", "text", "list"),
        "logic.if_then": MockSchema("logic.if_then", "logic", "bool"),
        "logic.compare": MockSchema("logic.compare", "logic", "bool"),
    }
    return MockRegistry(schemas)
