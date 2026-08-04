"""Phase 3b: Multi-Modal Reasoning Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]

REASONING_PROMPT = """You are a multi-modal reasoning engine. Analyze the task using multiple reasoning modes:

Context:
- Intent: {intent}
- Knowledge: {knowledge_summary}
- Attention: {attention_focus}

Analyze using:
1. Causal reasoning: What causes what?
2. Logical reasoning: What logically follows?
3. Probabilistic reasoning: What are likelihoods?
4. Common-sense reasoning: What makes intuitive sense?

Respond in format:
CAUSAL: <causal analysis>
LOGICAL: <logical conclusions>
PROBABILISTIC: <probability/likelihood assessment>
COMMON_SENSE: <intuitive/common-sense analysis>
CONCLUSION: <overall reasoning conclusion>
"""


def make_reasoning_node(llm: LLMFn):
    """Creates a node that performs multi-modal reasoning (Phase 3b)."""

    def process_reasoning(state: FullAgentState) -> FullAgentState:
        intent = state.get("intent", "")
        knowledge = state.get("knowledge_summary", "")
        attention = state.get("attention_focus", [])

        if not intent:
            return {
                "reasoning_type": "multi-modal",
                "reasoning_steps": [],
                "reasoning_conclusion": "",
            }

        attention_str = ", ".join(attention)

        prompt = REASONING_PROMPT.format(
            intent=intent,
            knowledge_summary=knowledge,
            attention_focus=attention_str,
        )

        response = llm(prompt).strip()

        # Parse response
        causal = ""
        logical = ""
        probabilistic = ""
        common_sense = ""
        conclusion = ""

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("CAUSAL:"):
                causal = line.split(":", 1)[1].strip()
            elif line.startswith("LOGICAL:"):
                logical = line.split(":", 1)[1].strip()
            elif line.startswith("PROBABILISTIC:"):
                probabilistic = line.split(":", 1)[1].strip()
            elif line.startswith("COMMON_SENSE:"):
                common_sense = line.split(":", 1)[1].strip()
            elif line.startswith("CONCLUSION:"):
                conclusion = line.split(":", 1)[1].strip()

        reasoning_steps = [causal, logical, probabilistic, common_sense]
        reasoning_steps = [s for s in reasoning_steps if s]

        return {
            "reasoning_type": "multi-modal",
            "reasoning_steps": reasoning_steps,
            "reasoning_conclusion": conclusion or response[:200],
        }

    return process_reasoning
