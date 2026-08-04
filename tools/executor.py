"""Tool execution engine with safety validation."""
from __future__ import annotations

import time
import logging
from typing import Any, Optional

from agents.state import ToolSchema, ToolExecutionResult
from tools.schema import ToolRegistry


class SafetyValidator:
    """Validates tool execution requests against safety policies."""

    def __init__(self):
        self.blocked_tools: set[str] = set()
        self.requires_confirmation: set[str] = set()
        self.network_access_allowed = False
        self.max_execution_time_seconds = 5.0

    def validate_execution(
        self, tool_schema: ToolSchema, parameters: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate a tool execution request.
        Returns (allowed, safety_violations).
        """
        violations = []

        # Check if tool is blocked
        if tool_schema.id in self.blocked_tools:
            violations.append(f"Tool {tool_schema.id} is blocked")

        # Check network access
        if tool_schema.requires_network and not self.network_access_allowed:
            violations.append("Network access not allowed")

        # Check parameter safety
        for param_schema in tool_schema.parameters:
            if param_schema.name in parameters:
                param_value = parameters[param_schema.name]
                is_valid, msg = param_schema.validate(param_value)
                if not is_valid:
                    violations.append(f"Parameter {param_schema.name}: {msg}")
            elif param_schema.required and param_schema.default is None:
                violations.append(f"Required parameter {param_schema.name} missing")

        return len(violations) == 0, violations


class ToolExecutor:
    """Executes tools with parameter binding and error handling."""

    def __init__(self, registry: ToolRegistry, safety_validator: SafetyValidator = None):
        self.registry = registry
        self.safety_validator = safety_validator or SafetyValidator()
        self.logger = logging.getLogger(__name__)

    def execute(
        self, tool_id: str, parameters: dict[str, Any], dry_run: bool = False
    ) -> ToolExecutionResult:
        """
        Execute a tool with given parameters.

        In dry_run mode, validates but doesn't execute.
        """
        start_time = time.time()

        # Retrieve tool
        tool_lookup = self.registry.get(tool_id)
        if not tool_lookup:
            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                error=f"Tool {tool_id} not found in registry",
            )

        tool_schema, tool_impl = tool_lookup

        # Parameter binding
        bound_params, binding_errors = self._bind_parameters(tool_schema, parameters)
        if binding_errors:
            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                error=f"Parameter binding failed: {'; '.join(binding_errors)}",
            )

        # Safety validation
        allowed, violations = self.safety_validator.validate_execution(tool_schema, bound_params)
        if not allowed:
            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                error="Safety validation failed",
                safety_violations=violations,
            )

        # Dry-run mode
        if dry_run:
            return ToolExecutionResult(
                tool_id=tool_id, success=True, value=None, execution_time_ms=0.0, confidence=0.0
            )

        # Actual execution
        try:
            result = tool_impl(**bound_params)
            elapsed_ms = (time.time() - start_time) * 1000

            return ToolExecutionResult(
                tool_id=tool_id,
                success=True,
                value=result,
                execution_time_ms=elapsed_ms,
                confidence=1.0,
            )

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.logger.exception(f"Tool {tool_id} execution failed")

            return ToolExecutionResult(
                tool_id=tool_id,
                success=False,
                error=str(e),
                execution_time_ms=elapsed_ms,
            )

    def _bind_parameters(
        self, tool_schema: ToolSchema, provided: dict[str, Any]
    ) -> tuple[dict[str, Any], list[str]]:
        """
        Bind provided parameters to tool schema.
        Returns (bound_params, errors).
        """
        bound = {}
        errors = []

        for param in tool_schema.parameters:
            if param.name in provided:
                value = provided[param.name]
                is_valid, msg = param.validate(value)
                if is_valid:
                    bound[param.name] = value
                else:
                    errors.append(f"{param.name}: {msg}")

            elif param.required:
                if param.default is not None:
                    bound[param.name] = param.default
                else:
                    errors.append(f"Required parameter {param.name} missing")

        return bound, errors
