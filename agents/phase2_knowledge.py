"""Phase 2: Knowledge Retrieval Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]

KNOWLEDGE_PROMPT = """Based on the following context:
- Intent: {intent}
- Entities: {entities}
- Summary: {summary}

Synthesize relevant knowledge and provide:
1. Key knowledge points related to the intent and entities
2. Summary of synthesized knowledge
3. Confidence in the knowledge

Respond in this format:
KNOWLEDGE_POINTS: <comma-separated key knowledge items>
SYNTHESIS: <synthesized knowledge summary>
CONFIDENCE: <0.0 to 1.0>
"""


def make_knowledge_node(llm: LLMFn):
    """Creates a node that retrieves and synthesizes knowledge (Phase 2)."""

    def process_knowledge(state: FullAgentState) -> FullAgentState:
        intent = state.get("intent", "")
        entities = state.get("entities", {})
        summary = state.get("summary", "")

        if not intent and not summary:
            return {
                "relevant_knowledge": [],
                "knowledge_summary": "",
            }

        entities_str = ", ".join(entities.get("names", []))

        prompt = KNOWLEDGE_PROMPT.format(
            intent=intent,
            entities=entities_str,
            summary=summary,
        )

        response = llm(prompt).strip()

        # Parse response
        knowledge_points = []
        synthesis = ""
        confidence = 0.5

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("KNOWLEDGE_POINTS:"):
                points_str = line.split(":", 1)[1].strip()
                knowledge_points = [p.strip() for p in points_str.split(",") if p.strip()]
            elif line.startswith("SYNTHESIS:"):
                synthesis = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass

        return {
            "relevant_knowledge": knowledge_points,
            "knowledge_summary": synthesis,
        }

    return process_knowledge
