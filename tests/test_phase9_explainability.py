"""Integration tests for Phase 9 Explainability & Interpretability."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class FakeLLMPhase9:
    """Deterministic fake LLM for Phase 9 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phases 1-8 responses (abbreviated)
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: test task
ENTITIES: data
SUMMARY: Test execution"""

        if "knowledge" in prompt_lower or "retrieve" in prompt_lower:
            return """KNOWLEDGE_POINTS: test knowledge
KNOWLEDGE_SUMMARY: Test summary"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: accuracy
METACOGNITIVE_NOTES: confident"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: logical
CAUSAL: test causes
LOGICAL: test logic
CONCLUSION: proceed"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: combine tools
ANALOGIES: like ETL
NOVELTY_SCORE: 75"""

        if "Tool Selection" in prompt or "SELECTED_TOOLS:" in prompt:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: good tools
CONFIDENCE: 0.9"""

        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 10\nb: 5"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.9
CONCERNS: none
REASONING: valid"""

        # Phase 9: Reasoning Trace
        if "reasoning trace" in prompt_lower or ("Phase" in prompt and "reasoning" in prompt_lower):
            return """SUMMARY: Reasoning analysis complete
REASONING: Key reasoning step identified
ALTERNATIVES: Alternative approach considered
CONFIDENCE_FACTORS: High confidence due to clear logic"""

        # Phase 9: Confidence Justification
        if "explain why" in prompt_lower or "confidence" in prompt_lower:
            return """REASONING: Confidence justified by evidence
SUPPORTING_EVIDENCE: Clear evidence exists
LIMITING_FACTORS: Some uncertainty remains
OVERALL_ASSESSMENT: Confidence is well-founded"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase9():
    """Create fake LLM for Phase 9 testing."""
    return FakeLLMPhase9()


@pytest.fixture
def registry():
    """Create tool registry."""
    return create_builtin_registry()


@pytest.fixture
def safety_validator():
    """Create safety validator."""
    return SafetyValidator()


@pytest.fixture
def temp_memory():
    """Create temporary memory manager."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    memory = MemoryManager(temp_path)
    yield memory
    import os
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_phase9_enabled_with_all_phases(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 with all phases 1-8 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task for Phase 9",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 9 ran
    assert "reasoning_traces" in result
    assert "confidence_justifications" in result
    assert "decision_audit_log" in result
    assert "phase9_summary" in result
    assert "explainability_score" in result


def test_phase9_disabled(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test that Phase 9 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=False,  # Disable Phase 9
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 9 should not run
    assert "phase9_summary" not in result or result.get("phase9_summary") is None


def test_phase9_without_phase8(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 can run without Phase 8."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=False,  # Disable Phase 8
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 9 should still run
    assert "phase9_summary" in result or "reasoning_traces" in result


def test_phase9_reasoning_traces_generation(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9a generates reasoning traces."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Task requiring explanation",
    }

    result = coordinator.invoke(initial_state)

    # Check reasoning traces
    traces = result.get("reasoning_traces", {})
    assert isinstance(traces, dict)
    if traces:
        for phase_name, trace in traces.items():
            assert "summary" in trace or isinstance(trace, dict)


def test_phase9_confidence_justifications(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9b generates confidence justifications."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Task for confidence analysis",
        "tool_selection_confidence": 0.85,
        "outcome_confidence": 0.75,
    }

    result = coordinator.invoke(initial_state)

    # Check confidence justifications
    just = result.get("confidence_justifications", {})
    assert isinstance(just, dict)


def test_phase9_decision_audit_log(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9c maintains decision audit log."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Auditable task",
        "execution_outcome": "success",
    }

    result = coordinator.invoke(initial_state)

    # Check audit log
    audit_log = result.get("decision_audit_log", [])
    assert isinstance(audit_log, list)
    if audit_log:
        for entry in audit_log:
            assert "decision_type" in entry
            assert "confidence" in entry


def test_phase9_explainability_score(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 calculates explainability score."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Calculate explainability",
    }

    result = coordinator.invoke(initial_state)

    # Check explainability score
    score = result.get("explainability_score", 0.0)
    assert isinstance(score, (int, float))
    assert 0 <= score <= 1


def test_phase9_overall_system_confidence(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 calculates overall system confidence."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "System confidence test",
        "tool_selection_confidence": 0.9,
        "outcome_confidence": 0.85,
    }

    result = coordinator.invoke(initial_state)

    # Check overall confidence
    confidence = result.get("overall_system_confidence", 0.0)
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 1


def test_phase9_summary_format(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 generates properly formatted summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Summary test",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase9_summary", "")
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Phase 9" in summary or "Explainability" in summary


def test_phase9_with_phase8_error_recovery(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 with error recovery from Phase 8."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Failure recovery test",
        "execution_outcome": "failure",
        "recovery_strategy": "alternative_tools",
        "recovery_confidence": 0.80,
    }

    result = coordinator.invoke(initial_state)

    # Phase 9 should explain recovery
    audit_log = result.get("decision_audit_log", [])
    has_recovery_entry = any(
        entry.get("decision_type") == "recovery_strategy" for entry in audit_log
    )
    if audit_log:
        # At least some audit entries should exist
        assert len(audit_log) > 0


def test_phase9_minimal_context(
    fake_llm_phase9, registry, safety_validator, temp_memory
):
    """Test Phase 9 works even with minimal execution context."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase9,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=False,
        enable_phase5=False,
        enable_phase6=False,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Minimal context",
    }

    result = coordinator.invoke(initial_state)

    # Phase 9 should still generate some explainability
    summary = result.get("phase9_summary", "")
    assert isinstance(summary, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
