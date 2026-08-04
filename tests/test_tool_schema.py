"""Tests for tool schema and registry."""
import pytest
from agents.state import ToolSchema, ToolParameter
from tools.schema import ToolRegistry


def test_tool_parameter_validation_success():
    """Test valid parameter validation."""
    param = ToolParameter(name="count", type="int", description="A count")
    is_valid, msg = param.validate(5)
    assert is_valid
    assert msg is None


def test_tool_parameter_validation_type_mismatch():
    """Test parameter type validation fails on wrong type."""
    param = ToolParameter(name="count", type="int", description="A count")
    is_valid, msg = param.validate("not an int")
    assert not is_valid
    assert "Expected int" in msg


def test_tool_parameter_validation_required():
    """Test required parameter validation."""
    param = ToolParameter(name="value", type="float", description="A value", required=True)
    is_valid, msg = param.validate(None)
    assert not is_valid


def test_tool_parameter_validation_enum():
    """Test enum value validation."""
    param = ToolParameter(
        name="operator",
        type="string",
        description="An operator",
        enum_values=[">", "<", "=="],
    )
    is_valid, msg = param.validate(">")
    assert is_valid

    is_valid, msg = param.validate("!=")
    assert not is_valid
    assert "not in allowed values" in msg


def test_tool_registry_register_and_get():
    """Test registering and retrieving tools."""
    registry = ToolRegistry()

    schema = ToolSchema(
        id="test.add",
        name="Add",
        description="Add two numbers",
        category="math",
        parameters=[
            ToolParameter(name="a", type="float", description="First number"),
            ToolParameter(name="b", type="float", description="Second number"),
        ],
        return_type="float",
        example_usage={"a": 1, "b": 2},
    )

    def add_impl(a: float, b: float) -> float:
        return a + b

    registry.register(schema, add_impl)

    result = registry.get("test.add")
    assert result is not None
    retrieved_schema, impl = result
    assert retrieved_schema.id == "test.add"
    assert impl(2, 3) == 5


def test_tool_registry_list_all():
    """Test listing all tools."""
    registry = ToolRegistry()

    for i in range(3):
        schema = ToolSchema(
            id=f"test.tool{i}",
            name=f"Tool {i}",
            description="Test tool",
            category="test",
            parameters=[],
            return_type="string",
            example_usage={},
        )
        registry.register(schema, lambda: None)

    tools = registry.list_all()
    assert len(tools) == 3


def test_tool_registry_get_by_capability():
    """Test filtering tools by capability."""
    registry = ToolRegistry()

    schema1 = ToolSchema(
        id="math.add",
        name="Add",
        description="Add numbers",
        category="math",
        parameters=[],
        return_type="float",
        example_usage={},
        capabilities=["arithmetic"],
    )

    schema2 = ToolSchema(
        id="text.upper",
        name="Uppercase",
        description="Convert text",
        category="text",
        parameters=[],
        return_type="string",
        example_usage={},
        capabilities=["text_transformation"],
    )

    registry.register(schema1, lambda: None)
    registry.register(schema2, lambda: None)

    arithmetic_tools = registry.get_by_capability("arithmetic")
    assert len(arithmetic_tools) == 1
    assert arithmetic_tools[0].id == "math.add"


def test_tool_registry_get_by_category():
    """Test filtering tools by category."""
    registry = ToolRegistry()

    for i in range(2):
        schema = ToolSchema(
            id=f"math.op{i}",
            name=f"Math Op {i}",
            description="Math operation",
            category="math",
            parameters=[],
            return_type="float",
            example_usage={},
        )
        registry.register(schema, lambda: None)

    math_tools = registry.get_by_category("math")
    assert len(math_tools) == 2


def test_tool_registry_serialize_for_llm():
    """Test LLM-friendly serialization."""
    registry = ToolRegistry()

    schema = ToolSchema(
        id="math.add",
        name="Add Numbers",
        description="Add two numbers",
        category="math",
        parameters=[
            ToolParameter(name="a", type="float", description="First"),
            ToolParameter(name="b", type="float", description="Second"),
        ],
        return_type="float",
        example_usage={"a": 1, "b": 2},
        capabilities=["arithmetic"],
    )

    registry.register(schema, lambda a, b: a + b)

    serialized = registry.serialize_for_llm()
    assert "math.add" in serialized
    assert "Add Numbers" in serialized
    assert "arithmetic" in serialized
    assert "Parameters:" in serialized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
