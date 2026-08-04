"""Phase 3c: Creativity Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]

CREATIVITY_PROMPT = """You are generating creative solutions and ideas.

Context:
- Intent: {intent}
- Reasoning: {reasoning_conclusion}
- Knowledge: {knowledge_summary}

Generate:
1. Novel creative ideas
2. Analogies from other domains
3. Creative combinations of concepts

Respond in format:
CREATIVE_IDEAS: <comma-separated novel ideas>
ANALOGIES: <comma-separated domain analogies>
CONCEPTUAL_BLEND: <creative concept combinations>
NOVELTY_SCORE: <0-100>
"""


def make_creativity_node(llm: LLMFn):
    """Creates a node that generates creative solutions (Phase 3c)."""

    def process_creativity(state: FullAgentState) -> FullAgentState:
        intent = state.get("intent", "")
        reasoning = state.get("reasoning_conclusion", "")
        knowledge = state.get("knowledge_summary", "")

        if not intent:
            return {
                "creative_ideas": [],
                "analogies": [],
                "novel_combinations": [],
            }

        prompt = CREATIVITY_PROMPT.format(
            intent=intent,
            reasoning_conclusion=reasoning,
            knowledge_summary=knowledge,
        )

        response = llm(prompt).strip()

        # Parse response
        creative_ideas = []
        analogies = []
        conceptual_blend = ""
        novelty_score = 50

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("CREATIVE_IDEAS:"):
                ideas_str = line.split(":", 1)[1].strip()
                creative_ideas = [i.strip() for i in ideas_str.split(",") if i.strip()]
            elif line.startswith("ANALOGIES:"):
                analogies_str = line.split(":", 1)[1].strip()
                analogies = [a.strip() for a in analogies_str.split(",") if a.strip()]
            elif line.startswith("CONCEPTUAL_BLEND:"):
                conceptual_blend = line.split(":", 1)[1].strip()
            elif line.startswith("NOVELTY_SCORE:"):
                try:
                    score_str = line.split(":", 1)[1].strip().rstrip("%")
                    novelty_score = int(score_str)
                    novelty_score = max(0, min(100, novelty_score))
                except ValueError:
                    novelty_score = 50

        return {
            "creative_ideas": creative_ideas,
            "analogies": analogies,
            "novel_combinations": [conceptual_blend] if conceptual_blend else [],
        }

    return process_creativity
