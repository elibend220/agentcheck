"""
test_graph.py

Verifies graph wiring, state propagation, and response parsing using a
deterministic fake LLM. This intentionally does not touch Ollama or any
real model: its job is to prove the orchestration logic is correct
independent of model quality, which is a separate, unverifiable-here
concern documented in README.md.
"""
from agent import build_graph, _parse_credibility_response


class FakeLLM:
    """Returns canned responses keyed by which prompt template was used,
    detected by a distinguishing substring, so the fake can answer
    differently for the summarize step versus the credibility step."""

    def __init__(self):
        self.calls: list[str] = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        if "SUMMARY:" in prompt and "SCORE:" not in prompt:
            return "The article reports that a local council approved a new budget."
        return "SCORE: 7\nRATIONALE: The summary attributes the claim to a named council session."


def test_graph_runs_both_nodes_in_order():
    fake = FakeLLM()
    graph = build_graph(fake)

    result = graph.invoke({
        "article_text": "A city council meeting concluded with budget approval.",
        "source_name": "Example Gazette",
    })

    assert len(fake.calls) == 2, "expected exactly one call per node"
    assert "summary" in result and result["summary"], "summarize node must populate summary"
    assert result["credibility_score"] == 7
    assert "named council session" in result["credibility_rationale"]


def test_credibility_score_is_clamped_to_valid_range():
    class OutOfRangeLLM:
        def __call__(self, prompt: str) -> str:
            if "SCORE:" in prompt:
                return "SCORE: 47\nRATIONALE: nonsense high value"
            return "a summary"

    graph = build_graph(OutOfRangeLLM())
    result = graph.invoke({"article_text": "text", "source_name": "x"})
    assert result["credibility_score"] == 10, "score must be clamped to the documented 1-10 range"


def test_malformed_credibility_response_falls_back_gracefully():
    score, rationale = _parse_credibility_response("not in the expected format at all")
    assert score == 5, "malformed responses must fall back to a neutral default, not raise"
    assert rationale


def test_state_is_not_mutated_across_independent_invocations():
    fake = FakeLLM()
    graph = build_graph(fake)

    first = graph.invoke({"article_text": "first article", "source_name": "A"})
    second = graph.invoke({"article_text": "second article", "source_name": "B"})

    assert first["summary"] == second["summary"], "fake returns the same canned summary"
    assert first is not second, "each invocation must return an independent state object"
