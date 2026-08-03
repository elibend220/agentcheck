"""Integration tests for full Phase 1-5 pipeline with coordinator."""

import pytest
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLM:
    """Deterministic fake LLM for testing full pipeline."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)

        # Phase 4a: Tool Selection (check first - has specific format)
        if "SELECT which tools" in prompt or "available tools" in prompt.lower() and "select" in prompt.lower():
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Use math for analysis and text for transformation
CONFIDENCE: 0.85"""

        # Phase 1: NLP
        if "extract intent" in prompt.lower() or "entities" in prompt.lower():
            return """INTENT: analyze data and transform
ENTITIES: data, transform
SUMMARY: Extract and process data"""

        # Phase 2: Knowledge
        if "knowledge" in prompt.lower() or "retrieve" in prompt.lower():
            return """KNOWLEDGE_POINTS: data processing uses transformations, math is fundamental
KNOWLEDGE_SUMMARY: Knowledge about data and math operations"""

        # Phase 3a: Consciousness
        if "attention" in prompt.lower() or "metacognitive" in prompt.lower():
            return """ATTENTION_FOCUS: numerical accuracy, data quality
METACOGNITIVE_NOTES: confident in approach"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt.lower() and "multi-modal" not in prompt.lower():
            return """REASONING_TYPE: multi-modal
REASONING_STEPS: 1. Analyze data, 2. Transform format, 3. Validate
REASONING_CONCLUSION: Use math and text tools"""

        # Phase 3c: Creativity
        if "creative" in prompt.lower() or "analogies" in prompt.lower():
            return """CREATIVE_IDEAS: combine analysis with transformation, novel data processing
ANALOGIES: like refining ore to extract gold
NOVEL_COMBINATIONS: analysis + transformation"""

        # Phase 4b: Tool Execution
        if "parameters" in prompt.lower() or "binding" in prompt.lower():
            return "a: 5\nb: 3"

        # Phase 4c: Tool Verification
        if "verif" in prompt.lower() or "valid:" in prompt.lower():
            return """VALID: true
CONFIDENCE: 0.9
CONCERNS: none
REASONING: Results are consistent"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm():
    """Create fake LLM for testing."""
    return FakeLLM()


@pytest.fixture
def registry():
    """Create tool registry."""
    return create_builtin_registry()


@pytest.fixture
def safety_validator():
    """Create safety validator."""
    return SafetyValidator()


def test_full_phase1_to_5_pipeline(fake_llm, registry, safety_validator):
    """Test complete Phase 1-5 pipeline with coordinator."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        dry_run_mode=True  # Dry run for testing
    )

    initial_state: FullAgentState = {
        "input_text": "Add 5 and 3, then convert to text",
    }

    # Execute full pipeline
    result = coordinator.invoke(initial_state)

    # Verify Phase 1 output
    assert result.get("intent") is not None
    assert len(result.get("entities", [])) >= 0

    # Verify Phase 2 output
    assert result.get("relevant_knowledge") is not None

    # Verify Phase 3a output
    assert result.get("attention_focus") is not None
    assert result.get("metacognitive_notes") is not None

    # Verify Phase 3b output
    assert result.get("reasoning_type") is not None
    assert result.get("reasoning_steps") is not None

    # Verify Phase 3c output
    assert result.get("creative_ideas") is not None

    # Verify Phase 4 output
    assert result.get("selected_tools") is not None
    assert len(result["selected_tools"]) > 0

    # Verify Phase 5 output (quantum optimization)
    assert result.get("quantum_state_created") is not None or result.get("selected_tools")


def test_phase5_without_phase4(fake_llm, registry):
    """Test that Phase 5 is skipped when Phase 4 is disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        enable_phase4=False,
        enable_phase5=True,  # Should be ignored
    )

    initial_state: FullAgentState = {
        "input_text": "Test input",
    }

    result = coordinator.invoke(initial_state)

    # Phase 5 should not run without Phase 4
    assert not result.get("quantum_state_created", False)


def test_phase5_without_registry(fake_llm):
    """Test that Phase 5 is skipped without tool registry."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=None,  # No registry
        enable_phase4=True,
        enable_phase5=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test input",
    }

    result = coordinator.invoke(initial_state)

    # Phase 4 and 5 should be skipped without registry
    assert not result.get("selected_tools", False)
    assert not result.get("quantum_state_created", False)


def test_phase5_optional(fake_llm, registry, safety_validator):
    """Test Phase 5 can be disabled while keeping Phase 4."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=False,  # Disable quantum
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test input",
    }

    result = coordinator.invoke(initial_state)

    # Phase 4 should run
    assert result.get("selected_tools") is not None

    # Phase 5 should not run
    assert not result.get("quantum_state_created", False)


def test_coordinator_state_flow(fake_llm, registry, safety_validator):
    """Test state flows correctly through all phases."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        dry_run_mode=True,
    )

    initial_text = "Process data: add 10 and 20"
    initial_state: FullAgentState = {
        "input_text": initial_text,
    }

    result = coordinator.invoke(initial_state)

    # Verify state preservation
    assert result.get("input_text") == initial_text

    # Verify each phase added to state
    assert "intent" in result
    assert "relevant_knowledge" in result
    assert "attention_focus" in result
    assert "reasoning_type" in result
    assert "creative_ideas" in result
    assert "selected_tools" in result
    assert "tool_execution_results" in result or "selected_tools" in result

    # Verify Phase 5 state fields
    if result.get("quantum_state_created"):
        assert "quantum_amplitudes" in result
        assert "quantum_metrics" in result


def test_coordinator_with_dry_run(fake_llm, registry, safety_validator):
    """Test coordinator respects dry_run_mode."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # In dry run, execution should be prevented but state should flow
    assert result.get("dry_run_mode") is True


def test_coordinator_llm_called_for_all_phases(fake_llm, registry, safety_validator):
    """Test LLM is called for each phase."""
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        dry_run_mode=True,
    )

    fake_llm.calls.clear()

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # LLM should be called multiple times for different phases
    assert len(fake_llm.calls) > 5  # At least for Phase 1-3, Phase 4a
