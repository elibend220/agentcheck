"""Tool schema, registry, and base classes."""
from __future__ import annotations

from typing import Callable, Optional
from agents.state import ToolSchema


class ToolRegistry:
    """Central registry for all available tools."""

    def __init__(self):
        self._tools: dict[str, tuple[ToolSchema, Callable]] = {}

    def register(self, schema: ToolSchema, impl: Callable) -> None:
        """Register a tool and its implementation."""
        self._tools[schema.id] = (schema, impl)

    def get(self, tool_id: str) -> Optional[tuple[ToolSchema, Callable]]:
        """Retrieve a tool by ID."""
        return self._tools.get(tool_id)

    def list_all(self) -> list[ToolSchema]:
        """Get all available tool schemas."""
        return [schema for schema, _ in self._tools.values()]

    def get_by_capability(self, capability: str) -> list[ToolSchema]:
        """Find tools that support a specific capability."""
        return [
            schema
            for schema, _ in self._tools.values()
            if capability in schema.capabilities
        ]

    def get_by_category(self, category: str) -> list[ToolSchema]:
        """Find tools in a specific category."""
        return [
            schema for schema, _ in self._tools.values()
            if schema.category == category
        ]

    def serialize_for_llm(self) -> str:
        """Format schemas for LLM consumption."""
        lines = ["Available Tools:"]
        for schema in self.list_all():
            lines.append(f"\n{schema.id}: {schema.name}")
            lines.append(f"  Description: {schema.description}")
            lines.append(f"  Category: {schema.category}")
            if schema.capabilities:
                lines.append(f"  Capabilities: {', '.join(schema.capabilities)}")
            if schema.parameters:
                lines.append("  Parameters:")
                for param in schema.parameters:
                    required = "required" if param.required else "optional"
                    lines.append(f"    - {param.name} ({param.type}, {required}): {param.description}")
            if schema.example_usage:
                lines.append(f"  Example: {schema.example_usage}")

        return "\n".join(lines)
