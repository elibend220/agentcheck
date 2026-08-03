"""Phase 4a: Tool Selection Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState
from tools.schema import ToolRegistry

LLMFn = Callable[[str], str]

TOOL_SELECTION_PROMPT = """You are the Tool Selection component of an integrated reasoning system.

Based on the following analysis from previous phases:
- Intent: {intent}
- Reasoning conclusion: {reasoning_conclusion}
- Creative ideas: {creative_ideas}
- Attention focus: {attention_focus}

And given these available tools:
{available_tools_description}

SELECT which tools would be most useful to achieve the goal. Consider:
1. Does each tool directly address the task?
2. Can tools be chained or combined?
3. Are there any safety or resource concerns?
4. What justifies this selection given the reasoning and creativity from prior phases?

Respond in this exact format:
SELECTED_TOOLS: tool_id1, tool_id2, tool_id3
REASONING: <brief explanation of why these tools, reflecting consciousness (attention-aware), reasoning (multi-modal justification), and creativity (novel combinations)>
CONFIDENCE: <0.0 to 1.0>
"""


def make_tool_selection_node(llm: LLMFn, registry: ToolRegistry):
    """
    Creates a node that selects which tools to use.

    Integrates consciousness (attention), reasoning (multi-modal),
    and creativity (novel combinations).
    """

    def select_tools(state: FullAgentState) -> FullAgentState:
        # Build prompt with available tools
        tools_description = registry.serialize_for_llm()

        prompt = TOOL_SELECTION_PROMPT.format(
            intent=state.get("intent", "unspecified"),
            reasoning_conclusion=state.get("reasoning_conclusion", ""),
            creative_ideas=", ".join(state.get("creative_ideas", [])),
            attention_focus=", ".join(state.get("attention_focus", [])),
            available_tools_description=tools_description,
        )

        # Get LLM selection
        response = llm(prompt).strip()

        # Parse response
        selected_ids, reasoning, confidence = _parse_tool_selection_response(response, registry)

        return {
            "selected_tools": selected_ids,
            "tool_selection_reasoning": reasoning,
            "tool_selection_confidence": confidence,
            "available_tools": registry.list_all(),
        }

    return select_tools


def _parse_tool_selection_response(
    response: str, registry: ToolRegistry
) -> tuple[list[str], str, float]:
    """Parse tool selection LLM response."""
    selected_ids = []
    reasoning = response
    confidence = 0.5  # default

    for line in response.splitlines():
        line = line.strip()

        if line.startswith("SELECTED_TOOLS:"):
            tool_ids_str = line.split(":", 1)[1].strip()
            selected_ids = [tid.strip() for tid in tool_ids_str.split(",") if tid.strip()]
            # Validate tool IDs exist in registry
            selected_ids = [tid for tid in selected_ids if registry.get(tid) is not None]

        elif line.startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()

        elif line.startswith("CONFIDENCE:"):
            try:
                conf_str = line.split(":", 1)[1].strip()
                confidence = float(conf_str)
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                confidence = 0.5

    return selected_ids, reasoning, confidence
