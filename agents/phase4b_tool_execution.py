"""Phase 4b: Tool Execution Agent."""
from __future__ import annotations

from typing import Callable, Any
from agents.state import FullAgentState, ToolSchema
from tools.schema import ToolRegistry
from tools.executor import ToolExecutor, SafetyValidator

LLMFn = Callable[[str], str]

PARAMETER_BINDING_PROMPT = """You are binding parameters for the following tool:

Tool: {tool_name}
Description: {tool_description}
Parameters needed: {parameters_list}

Based on the current state:
- Input: {input_text}
- Reasoning: {reasoning_conclusion}
- Attention: {attention_focus}

Provide parameter values in format: PARAM_NAME: value

Available parameters:
{parameter_descriptions}
"""


def make_tool_execution_node(
    llm: LLMFn, registry: ToolRegistry, safety_validator: SafetyValidator = None
):
    """
    Creates a node that executes selected tools.

    - Binds parameters using state extraction or defaults
    - Executes with safety validation
    - Handles errors gracefully
    - Supports dry-run mode
    """
    executor = ToolExecutor(registry, safety_validator or SafetyValidator())

    def execute_tools(state: FullAgentState) -> FullAgentState:
        selected_tool_ids = state.get("selected_tools", [])
        execution_results = []

        for tool_id in selected_tool_ids:
            tool_lookup = registry.get(tool_id)
            if not tool_lookup:
                continue

            tool_schema, _ = tool_lookup

            # Bind parameters
            parameters = _bind_parameters_for_tool(tool_schema, state)

            # Execute
            result = executor.execute(
                tool_id=tool_id,
                parameters=parameters,
                dry_run=state.get("dry_run_mode", False),
            )

            execution_results.append(result)

            # Track errors
            if not result.success:
                error_log = state.get("error_log", [])
                error_log.append(f"Tool {tool_id}: {result.error}")
                state["error_log"] = error_log

        return {"tool_execution_results": execution_results}

    return execute_tools


def _bind_parameters_for_tool(tool_schema: ToolSchema, state: FullAgentState) -> dict[str, Any]:
    """
    Intelligently bind parameters from state and defaults.

    Tries multiple strategies:
    1. Direct state extraction (if param name matches a state field)
    2. Use default values
    3. Parse from reasoning/input if applicable
    """
    parameters = {}

    for param in tool_schema.parameters:
        # Strategy 1: Direct state match
        if param.name in state and state[param.name] is not None:
            parameters[param.name] = state[param.name]
            continue

        # Strategy 2: Use default
        if param.default is not None:
            parameters[param.name] = param.default
            continue

        # Strategy 3: Try to infer from common fields
        # For "text" parameter, use input_text or summary
        if param.name == "text" and param.type == "string":
            if "summary" in state:
                parameters[param.name] = state["summary"]
            elif "input_text" in state:
                parameters[param.name] = state["input_text"]

        # For "value" parameter, try number fields
        if param.name in ["a", "b", "value"] and param.type in ["int", "float"]:
            # Look for numeric values in state
            for key in ["count", "score", "value", "number"]:
                if key in state and isinstance(state[key], (int, float)):
                    parameters[param.name] = state[key]
                    break

    return parameters
