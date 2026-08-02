"""Phase 1: NLP Processing Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]

NLP_PROMPT = """Analyze the following text and extract:
1. The main intent/goal
2. Key entities mentioned
3. A brief summary

TEXT:
{text}

Respond in this format:
INTENT: <primary goal or intent>
ENTITIES: <comma-separated list of key entities>
SUMMARY: <1-2 sentence summary>
"""


def make_nlp_node(llm: LLMFn):
    """Creates a node that performs NLP processing (Phase 1)."""

    def process_nlp(state: FullAgentState) -> FullAgentState:
        text = state.get("input_text", "")
        if not text:
            return {
                "intent": "",
                "entities": {},
                "summary": "",
            }

        prompt = NLP_PROMPT.format(text=text)
        response = llm(prompt).strip()

        # Parse response
        intent = ""
        entities = []
        summary = ""

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("INTENT:"):
                intent = line.split(":", 1)[1].strip()
            elif line.startswith("ENTITIES:"):
                entities_str = line.split(":", 1)[1].strip()
                entities = [e.strip() for e in entities_str.split(",") if e.strip()]
            elif line.startswith("SUMMARY:"):
                summary = line.split(":", 1)[1].strip()

        return {
            "intent": intent,
            "entities": {"names": entities},
            "summary": summary,
        }

    return process_nlp
