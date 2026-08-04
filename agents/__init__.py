"""Agents package for integrated AGI framework."""

from agents.state import (
    ToolParameter,
    ToolSchema,
    ToolExecutionResult,
    ToolVerificationResult,
    FullAgentState,
)
from agents.phase1_nlp import make_nlp_node
from agents.phase2_knowledge import make_knowledge_node
from agents.phase3a_consciousness import make_consciousness_node
from agents.phase3b_reasoning import make_reasoning_node
from agents.phase3c_creativity import make_creativity_node
from agents.phase4a_tool_selection import make_tool_selection_node
from agents.phase4b_tool_execution import make_tool_execution_node
from agents.phase4c_tool_verification import make_tool_verification_node
from agents.coordinator import AgentCoordinator

__all__ = [
    "ToolParameter",
    "ToolSchema",
    "ToolExecutionResult",
    "ToolVerificationResult",
    "FullAgentState",
    "make_nlp_node",
    "make_knowledge_node",
    "make_consciousness_node",
    "make_reasoning_node",
    "make_creativity_node",
    "make_tool_selection_node",
    "make_tool_execution_node",
    "make_tool_verification_node",
    "AgentCoordinator",
]
