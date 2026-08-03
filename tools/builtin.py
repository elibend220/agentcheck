"""Built-in tools library for Phase 4."""
from __future__ import annotations

import json
from agents.state import ToolSchema, ToolParameter
from tools.schema import ToolRegistry


# === Math Tools ===
def _add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


ADD_SCHEMA = ToolSchema(
    id="math.add",
    name="Add Numbers",
    description="Add two numbers and return the sum",
    category="math",
    parameters=[
        ToolParameter(name="a", type="float", description="First number"),
        ToolParameter(name="b", type="float", description="Second number"),
    ],
    return_type="float",
    example_usage={"a": 5, "b": 3},
    capabilities=["arithmetic", "numeric_operation"],
    example_output=8,
)


def _multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


MULTIPLY_SCHEMA = ToolSchema(
    id="math.multiply",
    name="Multiply Numbers",
    description="Multiply two numbers and return the product",
    category="math",
    parameters=[
        ToolParameter(name="a", type="float", description="First number"),
        ToolParameter(name="b", type="float", description="Second number"),
    ],
    return_type="float",
    example_usage={"a": 5, "b": 3},
    capabilities=["arithmetic", "numeric_operation"],
    example_output=15,
)


# === Text Tools ===
def _uppercase(text: str) -> str:
    """Convert text to uppercase."""
    return text.upper()


UPPERCASE_SCHEMA = ToolSchema(
    id="text.uppercase",
    name="Convert to Uppercase",
    description="Convert text to uppercase",
    category="text",
    parameters=[
        ToolParameter(name="text", type="string", description="Text to convert"),
    ],
    return_type="string",
    example_usage={"text": "hello world"},
    capabilities=["text_transformation"],
    example_output="HELLO WORLD",
)


def _lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


LOWERCASE_SCHEMA = ToolSchema(
    id="text.lowercase",
    name="Convert to Lowercase",
    description="Convert text to lowercase",
    category="text",
    parameters=[
        ToolParameter(name="text", type="string", description="Text to convert"),
    ],
    return_type="string",
    example_usage={"text": "HELLO WORLD"},
    capabilities=["text_transformation"],
    example_output="hello world",
)


def _split_text(text: str, separator: str = " ") -> list:
    """Split text by separator."""
    return text.split(separator)


SPLIT_TEXT_SCHEMA = ToolSchema(
    id="text.split",
    name="Split Text",
    description="Split text by a separator and return list of parts",
    category="text",
    parameters=[
        ToolParameter(name="text", type="string", description="Text to split"),
        ToolParameter(
            name="separator",
            type="string",
            description="Separator to split by",
            required=False,
            default=" ",
        ),
    ],
    return_type="list",
    example_usage={"text": "hello world", "separator": " "},
    capabilities=["text_processing"],
    example_output=["hello", "world"],
)


# === Logic Tools ===
def _if_then(condition: bool, true_value: str, false_value: str) -> str:
    """Return one of two values based on a condition."""
    return true_value if condition else false_value


IF_THEN_SCHEMA = ToolSchema(
    id="logic.if_then",
    name="Conditional Branch",
    description="Return one of two values based on a condition",
    category="logic",
    parameters=[
        ToolParameter(name="condition", type="bool", description="Condition to evaluate"),
        ToolParameter(name="true_value", type="string", description="Value if true"),
        ToolParameter(name="false_value", type="string", description="Value if false"),
    ],
    return_type="string",
    example_usage={"condition": True, "true_value": "yes", "false_value": "no"},
    capabilities=["branching", "conditional_logic"],
    example_output="yes",
)


def _compare(a: float, b: float, operator: str = ">") -> bool:
    """Compare two values."""
    ops = {
        ">": lambda x, y: x > y,
        "<": lambda x, y: x < y,
        ">=": lambda x, y: x >= y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y,
        "!=": lambda x, y: x != y,
    }
    op_func = ops.get(operator)
    if not op_func:
        raise ValueError(f"Unknown operator: {operator}")
    return op_func(a, b)


COMPARE_SCHEMA = ToolSchema(
    id="logic.compare",
    name="Compare Values",
    description="Compare two values using an operator",
    category="logic",
    parameters=[
        ToolParameter(name="a", type="float", description="First value"),
        ToolParameter(name="b", type="float", description="Second value"),
        ToolParameter(
            name="operator",
            type="string",
            description="Comparison operator",
            required=False,
            default=">",
            enum_values=[">", "<", ">=", "<=", "==", "!="],
        ),
    ],
    return_type="bool",
    example_usage={"a": 5, "b": 3, "operator": ">"},
    capabilities=["comparison", "conditional_logic"],
    example_output=True,
)


# === Data Tools ===
def _parse_json(json_string: str) -> dict:
    """Parse JSON string into a dict."""
    return json.loads(json_string)


PARSE_JSON_SCHEMA = ToolSchema(
    id="data.parse_json",
    name="Parse JSON",
    description="Parse a JSON string into a Python dict",
    category="data",
    parameters=[
        ToolParameter(name="json_string", type="string", description="JSON text to parse"),
    ],
    return_type="dict",
    example_usage={"json_string": '{"key": "value"}'},
    capabilities=["data_parsing", "json_handling"],
    example_output={"key": "value"},
)


def _stringify_json(obj: dict) -> str:
    """Convert a dict to JSON string."""
    return json.dumps(obj, indent=2)


STRINGIFY_JSON_SCHEMA = ToolSchema(
    id="data.stringify_json",
    name="Stringify JSON",
    description="Convert a Python dict to a JSON string",
    category="data",
    parameters=[
        ToolParameter(name="obj", type="dict", description="Object to stringify"),
    ],
    return_type="string",
    example_usage={"obj": {"key": "value"}},
    capabilities=["data_serialization", "json_handling"],
    example_output='{\n  "key": "value"\n}',
)


def create_builtin_registry() -> ToolRegistry:
    """Create registry with all built-in tools."""
    registry = ToolRegistry()

    # Math tools
    registry.register(ADD_SCHEMA, _add)
    registry.register(MULTIPLY_SCHEMA, _multiply)

    # Text tools
    registry.register(UPPERCASE_SCHEMA, _uppercase)
    registry.register(LOWERCASE_SCHEMA, _lowercase)
    registry.register(SPLIT_TEXT_SCHEMA, _split_text)

    # Logic tools
    registry.register(IF_THEN_SCHEMA, _if_then)
    registry.register(COMPARE_SCHEMA, _compare)

    # Data tools
    registry.register(PARSE_JSON_SCHEMA, _parse_json)
    registry.register(STRINGIFY_JSON_SCHEMA, _stringify_json)

    return registry
