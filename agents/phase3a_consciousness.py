"""Phase 3a: Consciousness Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]

CONSCIOUSNESS_PROMPT = """You are assessing consciousness and awareness for a reasoning system.

Context:
- Intent: {intent}
- Knowledge: {knowledge_summary}
- Prior reasoning: {reasoning_conclusion}

Analyze:
1. What should the system focus attention on?
2. What metacognitive insights are relevant?
3. How confident is the system in its understanding?

Respond in format:
ATTENTION_FOCUS: <comma-separated key focus areas>
METACOGNITION: <self-aware insights about reasoning limitations/strengths>
CONFIDENCE: <0.0 to 1.0>
"""


def make_consciousness_node(llm: LLMFn):
    """Creates a node that processes consciousness and metacognition (Phase 3a)."""

    def process_consciousness(state: FullAgentState) -> FullAgentState:
        intent = state.get("intent", "")
        knowledge = state.get("knowledge_summary", "")
        reasoning = state.get("reasoning_conclusion", "")

        if not intent:
            return {
                "attention_focus": [],
                "metacognitive_notes": "",
            }

        prompt = CONSCIOUSNESS_PROMPT.format(
            intent=intent,
            knowledge_summary=knowledge,
            reasoning_conclusion=reasoning,
        )

        response = llm(prompt).strip()

        # Parse response
        attention_focus = []
        metacognition = ""
        confidence = 0.5

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("ATTENTION_FOCUS:"):
                focus_str = line.split(":", 1)[1].strip()
                attention_focus = [f.strip() for f in focus_str.split(",") if f.strip()]
            elif line.startswith("METACOGNITION:"):
                metacognition = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass

        return {
            "attention_focus": attention_focus,
            "metacognitive_notes": metacognition,
        }

    return process_consciousness
