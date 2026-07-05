"""
agent.py

Two node LangGraph pipeline: summarize an article, then score the
credibility of its source based on the summary and a small set of
explicit heuristics.

The LLM is injected as a plain callable: `Callable[[str], str]`. This is
deliberate. It decouples the graph's control flow, state transitions, and
node sequencing, the part that can be wrong independently of any model,
from the actual language model backend. It also means the graph's wiring
can be verified with a deterministic fake in unit tests without requiring
a running model server, see tests/test_graph.py.
"""
from __future__ import annotations

from typing import Callable, TypedDict

from langgraph.graph import StateGraph, END


LLMFn = Callable[[str], str]


class AgentState(TypedDict, total=False):
    article_text: str
    source_name: str
    summary: str
    credibility_score: int
    credibility_rationale: str


SUMMARIZE_PROMPT = """Summarize the following article in three sentences \
or fewer. Be factual, do not add opinions or information not present in \
the text.

ARTICLE:
{article_text}

SUMMARY:"""

CREDIBILITY_PROMPT = """You are assessing the likely credibility of a news \
source based on a summary of one of its articles, not on the topic itself.

Consider only these factors: presence of specific named sources or \
attributions, presence of hedging language versus unsupported absolute \
claims, and internal consistency of the summary.

Respond in exactly this format:
SCORE: <integer from 1 to 10>
RATIONALE: <one sentence, referencing which factor drove the score>

SOURCE: {source_name}
SUMMARY:
{summary}
"""


def make_summarize_node(llm: LLMFn):
    def summarize(state: AgentState) -> AgentState:
        prompt = SUMMARIZE_PROMPT.format(article_text=state["article_text"])
        summary = llm(prompt).strip()
        return {"summary": summary}
    return summarize


def make_credibility_node(llm: LLMFn):
    def score_credibility(state: AgentState) -> AgentState:
        prompt = CREDIBILITY_PROMPT.format(
            source_name=state.get("source_name", "unknown"),
            summary=state["summary"],
        )
        raw = llm(prompt).strip()
        score, rationale = _parse_credibility_response(raw)
        return {"credibility_score": score, "credibility_rationale": rationale}
    return score_credibility


def _parse_credibility_response(raw: str) -> tuple[int, str]:
    """Parse the SCORE/RATIONALE format. Falls back to a conservative
    default rather than raising, since this runs inside a graph node and
    a malformed model response should degrade gracefully, not crash the
    pipeline."""
    score = 5
    rationale = raw or "Model returned an empty or unparseable response."
    for line in raw.splitlines():
        line = line.strip()
        if line.upper().startswith("SCORE:"):
            digits = "".join(c for c in line.split(":", 1)[1] if c.isdigit())
            if digits:
                score = max(1, min(10, int(digits)))
        elif line.upper().startswith("RATIONALE:"):
            rationale = line.split(":", 1)[1].strip()
    return score, rationale


def build_graph(llm: LLMFn):
    """Constructs the compiled LangGraph: summarize -> score_credibility -> END."""
    graph = StateGraph(AgentState)
    graph.add_node("summarize", make_summarize_node(llm))
    graph.add_node("score_credibility", make_credibility_node(llm))
    graph.set_entry_point("summarize")
    graph.add_edge("summarize", "score_credibility")
    graph.add_edge("score_credibility", END)
    return graph.compile()
