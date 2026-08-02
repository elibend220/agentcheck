"""Tests for tool execution engine."""
import pytest
from agents.state import ToolSchema, ToolParameter
from tools.schema import ToolRegistry
from tools.executor import ToolExecutor, SafetyValidator


def create_test_registry():
    """Create a test registry with sample tools."""
    registry = ToolRegistry()

    def add_impl(a: float, b: float) -> float:
        return a + b

    add_schema = ToolSchema(
        id="math.add",
        name="Add",
        description="Add two numbers",
        category="math",
        parameters=[
            ToolParameter(name="a", type="float", description="First"),
            ToolParameter(name="b", type="float", description="Second"),
        ],
        return_type="float",
        example_usage={"a": 1, "b": 2},
    )

    registry.register(add_schema, add_impl)
    return registry


def test_executor_execute_success():
    """Test successful tool execution."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("math.add", {"a": 2.0, "b": 3.0})

    assert result.success
    assert result.value == 5.0
    assert result.error is None
    assert result.confidence == 1.0


def test_executor_execute_missing_tool():
    """Test execution fails for missing tool."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("nonexistent.tool", {})

    assert not result.success
    assert "not found" in result.error


def test_executor_execute_missing_parameter():
    """Test execution fails for missing required parameter."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("math.add", {"a": 2.0})  # missing 'b'

    assert not result.success
    assert "missing" in result.error.lower()


def test_executor_execute_dry_run():
    """Test dry-run mode doesn't execute."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("math.add", {"a": 2.0, "b": 3.0}, dry_run=True)

    assert result.success
    assert result.value is None
    assert result.confidence == 0.0  # dry-run has low confidence


def test_executor_execute_parameter_type_mismatch():
    """Test execution fails for type mismatch."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("math.add", {"a": "not a number", "b": 3.0})

    assert not result.success
    assert "parameter" in result.error.lower()


def test_safety_validator_blocks_tool():
    """Test safety validator can block tools."""
    validator = SafetyValidator()
    validator.blocked_tools.add("dangerous.tool")

    schema = ToolSchema(
        id="dangerous.tool",
        name="Dangerous",
        description="Dangerous tool",
        category="test",
        parameters=[],
        return_type="string",
        example_usage={},
    )

    allowed, violations = validator.validate_execution(schema, {})

    assert not allowed
    assert len(violations) > 0


def test_safety_validator_network_access():
    """Test safety validator checks network access."""
    validator = SafetyValidator()
    validator.network_access_allowed = False

    schema = ToolSchema(
        id="web.fetch",
        name="Fetch",
        description="Fetch from web",
        category="web",
        parameters=[],
        return_type="string",
        example_usage={},
        requires_network=True,
    )

    allowed, violations = validator.validate_execution(schema, {})

    assert not allowed
    assert any("network" in v.lower() for v in violations)


def test_executor_parameter_binding():
    """Test parameter binding strategy."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    tool_lookup = registry.get("math.add")
    schema, _ = tool_lookup

    # Test binding with provided parameters
    bound, errors = executor._bind_parameters(schema, {"a": 1.0, "b": 2.0})
    assert not errors
    assert bound["a"] == 1.0
    assert bound["b"] == 2.0


def test_executor_execution_time_tracking():
    """Test execution time is tracked."""
    registry = create_test_registry()
    executor = ToolExecutor(registry)

    result = executor.execute("math.add", {"a": 1.0, "b": 2.0})

    assert result.success
    assert result.execution_time_ms >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
