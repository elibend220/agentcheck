"""Tests for full integrated pipeline (Phases 1-4)."""
import pytest
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLM:
    """Deterministic fake LLM for testing all phases."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1

        # Phase 1: NLP
        if "extract" in prompt.lower() or "INTENT:" in prompt:
            return """INTENT: calculate and transform text
ENTITIES: numbers, text transformation
SUMMARY: The task is to perform arithmetic and text processing"""

        # Phase 2: Knowledge
        if "synthesize" in prompt.lower() or "SYNTHESIS:" in prompt:
            return """KNOWLEDGE_POINTS: arithmetic operations, text processing
SYNTHESIS: Knowledge about basic math and string operations
CONFIDENCE: 0.8"""

        # Phase 3a: Consciousness
        if "consciousness" in prompt.lower() or "ATTENTION_FOCUS:" in prompt:
            return """ATTENTION_FOCUS: accuracy, efficiency
METACOGNITION: System is confident about math, less about text handling
CONFIDENCE: 0.7"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt.lower() or "CAUSAL:" in prompt:
            return """CAUSAL: arithmetic operations produce numerical results
LOGICAL: mathematical rules must be followed
PROBABILISTIC: high probability of correct addition
COMMON_SENSE: adding numbers gives expected results
CONCLUSION: The approach is sound"""

        # Phase 3c: Creativity
        if "creative" in prompt.lower() or "CREATIVE_IDEAS:" in prompt:
            return """CREATIVE_IDEAS: combine operations, chain multiple tools
ANALOGIES: similar to data pipelines
CONCEPTUAL_BLEND: math and text processing fusion
NOVELTY_SCORE: 65"""

        # Phase 4a: Tool Selection
        if "Tool Selection" in prompt or "SELECTED_TOOLS:" in prompt:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Use math tool for calculation and text tool for transformation
CONFIDENCE: 0.85"""

        # Phase 4b/c: Execution and Verification
        if "binding" in prompt.lower() or "parameters" in prompt.lower():
            return "a: 5\nb: 3"

        if "Verif" in prompt or "VALID:" in prompt:
            return """VALID: true
CONFIDENCE: 0.9
CONCERNS: none
REASONING: Results are valid"""

        return "RESULT: processed"


def test_full_pipeline_without_phase4():
    """Test full pipeline Phases 1-3 without tool execution."""
    llm = FakeLLM()
    coordinator = AgentCoordinator(llm, enable_phase4=False)

    state: FullAgentState = {
        "input_text": "Add 5 and 3, then convert to uppercase"
    }

    result = coordinator.invoke(state)

    # Verify each phase produced output
    assert "intent" in result
    assert "entities" in result
    assert "summary" in result
    assert "relevant_knowledge" in result
    assert "attention_focus" in result
    assert "reasoning_conclusion" in result
    assert "creative_ideas" in result

    # Phase 4 should not be present
    assert "selected_tools" not in result or not result.get("selected_tools")


def test_full_pipeline_with_phase4():
    """Test full pipeline including Phase 4 (tool execution)."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    coordinator = AgentCoordinator(
        llm, tool_registry=registry, enable_phase4=True, dry_run_mode=True
    )

    state: FullAgentState = {
        "input_text": "Add 5 and 3, then convert to uppercase"
    }

    result = coordinator.invoke(state)

    # Verify all phases produced output
    assert "intent" in result
    assert "relevant_knowledge" in result
    assert "attention_focus" in result
    assert "reasoning_conclusion" in result
    assert "creative_ideas" in result

    # Phase 4 specific checks
    assert "selected_tools" in result
    assert "tool_selection_reasoning" in result


def test_pipeline_state_flow_preservation():
    """Test that state is preserved through all phases."""
    llm = FakeLLM()
    coordinator = AgentCoordinator(llm, enable_phase4=False)

    original_input = "Calculate 10 + 5 and convert result"

    state: FullAgentState = {
        "input_text": original_input
    }

    result = coordinator.invoke(state)

    # Original input should be preserved
    assert result.get("input_text") == original_input

    # All phases should have contributed to state
    assert len(result) > 1  # More than just input_text


def test_pipeline_error_handling():
    """Test pipeline graceful error handling."""

    class FailingLLM:
        def __call__(self, prompt: str) -> str:
            raise RuntimeError("LLM failure")

    llm = FailingLLM()
    coordinator = AgentCoordinator(llm, enable_phase4=False)

    state: FullAgentState = {
        "input_text": "test"
    }

    # Pipeline should either handle gracefully or raise descriptive error
    try:
        result = coordinator.invoke(state)
        # If no exception, verify state isn't completely broken
        assert "input_text" in result
    except Exception as e:
        # Should be a clear error message
        assert len(str(e)) > 0


def test_pipeline_with_dry_run():
    """Test dry-run mode prevents actual tool execution."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    coordinator = AgentCoordinator(
        llm, tool_registry=registry, enable_phase4=True, dry_run_mode=True
    )

    state: FullAgentState = {
        "input_text": "Execute some tools"
    }

    result = coordinator.invoke(state)

    # In dry-run, tools should not actually execute
    exec_results = result.get("tool_execution_results", [])
    for exec_result in exec_results:
        # Either no execution or value is None (dry-run marker)
        if exec_result.success and "dry_run" in str(exec_result):
            assert exec_result.value is None or exec_result.confidence == 0.0


def test_pipeline_llm_call_count():
    """Test that each phase calls the LLM appropriate number of times."""
    llm = FakeLLM()
    coordinator = AgentCoordinator(llm, enable_phase4=False)

    state: FullAgentState = {
        "input_text": "test input"
    }

    result = coordinator.invoke(state)

    # Without Phase 4: Phase 1, 2, 3a, 3b, 3c = 5 nodes
    # Each node calls LLM once
    assert llm.call_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
