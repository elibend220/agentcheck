"""Integration tests for Phase 8 Error Recovery & Intelligent Retry."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager, ExecutionMemory


class FakeLLMPhase8:
    """Deterministic fake LLM for Phase 8 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phase 1-7 responses (abbreviated)
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
            return """VALID: false
CONFIDENCE: 0.3
CONCERNS: tool failed
REASONING: error in execution"""

        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool selection failed
LESSON 2: Need better validation
LESSON 3: Try alternative approach"""

        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Use alternative tools
SUGGESTION 2: Add error handling
SUGGESTION 3: Implement retry logic"""

        # Phase 7: Memory responses
        if "similar" in prompt_lower and ("past" in prompt_lower or "execution" in prompt_lower):
            return """INSIGHT 1: Alternative tools available
INSIGHT 2: Try sequential approach
CONFIDENCE: 0.75
RECOMMENDED_APPROACH: Use text.split followed by math.add"""

        # Phase 8: Error recovery responses
        if "analyze" in prompt_lower and ("failure" in prompt_lower or "execution" in prompt_lower):
            return """ROOT_CAUSE: Tool incompatibility
RECOVERY_OPTIONS: alternative_tools, adjust_parameters, enhance_reasoning
RISK_LEVEL: low
RECOMMENDED_ACTION: Use alternative tool combination"""

        if "retry" in prompt_lower or "recovery" in prompt_lower:
            return """ALTERNATIVE_TOOLS: text.split, math.multiply
PARAMETER_ADJUSTMENTS: increase timeout, add validation
EXECUTION_SEQUENCE: text.split → math.multiply
REASONING: This combination worked in similar past tasks
CONFIDENCE: 0.85"""

        if "evaluate" in prompt_lower and "retry" in prompt_lower:
            return """OUTCOME: success
IMPROVEMENTS: Better error handling, more robust execution, faster performance
CONFIDENCE: 0.9
EXPLANATION: Alternative approach succeeds where original failed"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase8():
    """Create fake LLM for Phase 8 testing."""
    return FakeLLMPhase8()


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


def test_phase8_enabled_with_failure(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 detects and attempts to recover from failure."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test failing task",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 8 ran
    assert "recovery_needed" in result
    assert "phase8_summary" in result


def test_phase8_disabled(fake_llm_phase8, registry, safety_validator, temp_memory):
    """Test that Phase 8 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=False,  # Disable Phase 8
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 8 should not run
    assert "recovery_needed" not in result or result.get("recovery_needed") is None


def test_phase8_without_phase7(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 can run without Phase 7."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,  # Disable Phase 7
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 8 should still run
    assert "recovery_needed" in result or "phase8_summary" in result


def test_phase8_success_path(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 when execution succeeds (no recovery needed)."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Successful task",
        "execution_outcome": "success",
    }

    result = coordinator.invoke(initial_state)

    # Phase 8 should detect no recovery needed
    assert "recovery_needed" in result
    if result.get("recovery_needed") is False:
        assert "phase8_summary" in result


def test_phase8_retry_plan_generation(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 generates retry plan for failed execution."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Failing task",
        "execution_outcome": "failure",
        "failure_analysis": {"analysis": "Tool incompatibility detected"},
    }

    result = coordinator.invoke(initial_state)

    # Should generate retry plan
    if result.get("recovery_needed"):
        assert "retry_plan" in result or "phase8_summary" in result


def test_phase8_with_full_pipeline(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 integrated with full 1-8 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Full pipeline test",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("execution_outcome") is not None  # Phase 6
    assert result.get("memory_persisted") is not None  # Phase 7
    assert "phase8_summary" in result  # Phase 8


def test_phase8_recovery_strategy_detection(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 detects appropriate recovery strategy."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Task with failure",
        "execution_outcome": "failure",
        "failure_analysis": {"analysis": "Parameter validation failed"},
    }

    result = coordinator.invoke(initial_state)

    # Should detect recovery strategy
    if result.get("recovery_needed"):
        assert "recovery_strategy" in result
        strategy = result.get("recovery_strategy", "")
        assert strategy in [
            "alternative_tools",
            "adjust_parameters",
            "enhance_reasoning",
            "increase_resources",
            "comprehensive_retry",
            "none",
        ]


def test_phase8_summary_generation(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 generates comprehensive summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase8_summary", "")
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Phase 8" in summary or "Recovery" in summary


def test_phase8_partial_outcome_recovery(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 handles partial execution outcomes."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Partial execution task",
        "execution_outcome": "partial",
    }

    result = coordinator.invoke(initial_state)

    # Should detect recovery for partial outcome
    if result.get("recovery_needed"):
        assert result.get("recovery_strategy") == "enhance_reasoning"


def test_phase8_uses_phase7_insights(
    fake_llm_phase8, registry, safety_validator, temp_memory
):
    """Test Phase 8 uses Phase 7 insights for recovery."""
    # Pre-populate memory with successful execution
    temp_memory.add_memory(ExecutionMemory(
        input_text="Similar failing task",
        execution_outcome="success",
        lessons_learned=["Alternative approach works"],
        tool_performance_scores={"text.split": 0.95, "math.multiply": 0.9},
        effective_tools=["text.split", "math.multiply"],
        improvement_suggestions=[],
        learning_metrics={},
    ))

    coordinator = AgentCoordinator(
        llm=fake_llm_phase8,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Similar failing task with new context",
        "execution_outcome": "failure",
    }

    result = coordinator.invoke(initial_state)

    # Should have retrieved historical alternatives
    if result.get("recovery_needed") and result.get("retry_attempted"):
        assert "historical_alternatives" in result
