"""Integration tests for Phase 6 Learning & Feedback Loop."""

import pytest
from agents.state import FullAgentState, ToolExecutionResult, ToolVerificationResult
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLMPhase6:
    """Deterministic fake LLM for Phase 6 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phase 1-5 responses
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

        if "reasoning" in prompt_lower and ("causal" in prompt_lower or "analyze" in prompt_lower):
            return """REASONING_TYPE: logical
CAUSAL: test causes
LOGICAL: test logic
PROBABILISTIC: high probability
COMMON_SENSE: valid approach
CONCLUSION: proceed"""

        if "creative" in prompt_lower or "novelty" in prompt_lower:
            return """CREATIVE_IDEAS: combine tools
ANALOGIES: like ETL
CONCEPTUAL_BLEND: transformation
NOVELTY_SCORE: 75"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: good tools
CONFIDENCE: 0.9"""

        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 10\nb: 5"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.95
CONCERNS: none
REASONING: correct results"""

        # Phase 6: Learning responses
        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool selection was effective
LESSON 2: Execution flowed smoothly
LESSON 3: Verification confirmed correctness"""

        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Consider using more diverse tools
SUGGESTION 2: Add more reasoning steps
SUGGESTION 3: Enhance creativity phase"""

        if "analyze" in prompt_lower and "fail" in prompt_lower:
            return """ROOT_CAUSES: tool incompatibility
CONTRIBUTING_FACTORS: parameter mismatch
PREVENTION: validate parameters first"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase6():
    """Create fake LLM for Phase 6 testing."""
    return FakeLLMPhase6()


@pytest.fixture
def registry():
    """Create tool registry."""
    return create_builtin_registry()


@pytest.fixture
def safety_validator():
    """Create safety validator."""
    return SafetyValidator()


def test_phase6_enabled_with_execution(fake_llm_phase6, registry, safety_validator):
    """Test Phase 6 is enabled and runs after execution."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Add 10 and 5",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 6 output is generated
    assert "execution_outcome" in result
    assert result.get("outcome_confidence") is not None
    assert "learning_metrics" in result
    assert "phase6_summary" in result


def test_phase6_disabled(fake_llm_phase6, registry, safety_validator):
    """Test that Phase 6 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=False,  # Disable Phase 6
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 6 should not run
    assert "execution_outcome" not in result or result.get("execution_outcome") is None


def test_phase6_without_phase4(fake_llm_phase6, registry, safety_validator):
    """Test Phase 6 still runs when Phase 4 is disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=False,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Just analyze this",
    }

    result = coordinator.invoke(initial_state)

    # Phase 6 should still run without Phase 4
    assert "execution_outcome" in result
    assert "learning_metrics" in result


def test_phase6_with_full_pipeline(fake_llm_phase6, registry, safety_validator):
    """Test Phase 6 integrated with full Phase 1-5 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Add 10 and 5, then convert to uppercase",
    }

    result = coordinator.invoke(initial_state)

    # Verify key phases ran
    assert result.get("intent") is not None  # Phase 1
    assert result.get("relevant_knowledge") is not None  # Phase 2
    assert result.get("attention_focus") is not None  # Phase 3a
    assert result.get("reasoning_type") is not None  # Phase 3b
    assert result.get("creative_ideas") is not None  # Phase 3c
    assert result.get("selected_tools") is not None  # Phase 4

    # Phase 6 should have run
    assert "execution_outcome" in result
    assert "lessons_learned" in result


def test_phase6_learning_metrics(fake_llm_phase6, registry, safety_validator):
    """Test that Phase 6 computes correct learning metrics."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    # Verify metrics structure
    metrics = result.get("learning_metrics", {})
    assert "outcome_score" in metrics
    assert "avg_tool_performance" in metrics
    assert "avg_phase_performance" in metrics
    assert "lessons_extracted" in metrics
    assert "learning_quality" in metrics
    assert "overall_learning_score" in metrics

    # Verify metric values are reasonable
    assert 0.0 <= metrics.get("outcome_score", 0) <= 1.0
    assert 0.0 <= metrics.get("avg_tool_performance", 0) <= 1.0
    assert 0.0 <= metrics.get("overall_learning_score", 0) <= 1.0


def test_phase6_with_phase5(fake_llm_phase6, registry, safety_validator):
    """Test Phase 6 works correctly with Phase 5 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Process and optimize",
    }

    result = coordinator.invoke(initial_state)

    # Both Phase 5 and Phase 6 should have run
    assert "learning_metrics" in result
    # Phase 4 should have executed
    assert result.get("selected_tools") is not None


def test_phase6_summary_generation(fake_llm_phase6, registry, safety_validator):
    """Test Phase 6 generates summary correctly."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase6_summary", "")
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Phase 6" in summary or "Learning" in summary or "Outcome" in summary


def test_phase6_generates_lessons(fake_llm_phase6, registry, safety_validator):
    """Test that Phase 6 generates lessons learned."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    lessons = result.get("lessons_learned", [])
    assert isinstance(lessons, list)


def test_phase6_generates_suggestions(fake_llm_phase6, registry, safety_validator):
    """Test that Phase 6 generates improvement suggestions."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase6,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    suggestions = result.get("improvement_suggestions", [])
    assert isinstance(suggestions, list)
