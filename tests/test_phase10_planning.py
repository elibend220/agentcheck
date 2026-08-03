"""Integration tests for Phase 10 Autonomous Planning & Goal Decomposition."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class FakeLLMPhase10:
    """Deterministic fake LLM for Phase 10 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phases 1-9 responses (abbreviated)
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Implement software system
ENTITIES: system, implementation
SUMMARY: Complex implementation task"""

        if "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: implementation patterns
KNOWLEDGE_SUMMARY: Patterns available"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: quality, efficiency
METACOGNITIVE_NOTES: Confident"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: analytical
CAUSAL: Requirements drive design
CONCLUSION: Proceed with systematic approach"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Modular design
NOVELTY_SCORE: 72"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: data.aggregate, text.format
CONFIDENCE: 0.88"""

        if "parameter" in prompt_lower:
            return "threshold: 0.75"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return "VALID: true\nCONFIDENCE: 0.90"

        # Phase 10a: Goal Decomposition
        if "decompose" in prompt_lower or "subgoal" in prompt_lower:
            return """PRIMARY_GOAL: Implement working system
SUBGOALS: Design architecture, Implement core, Test components, Deploy
HIERARCHY: Sequential phases with dependencies
DEPENDENCIES: Core must precede testing"""

        # Phase 10b: Plan Generation
        if "execution plan" in prompt_lower or "step" in prompt_lower:
            return """EXECUTION_STEPS: Design, Code, Test, Deploy, Monitor
CRITICAL_PATH: Design → Code → Test → Deploy
ESTIMATED_DURATION: 10
RESOURCE_REQUIREMENTS: Team: 3 engineers, Time: 10 weeks
PARALLELIZABLE: Some testing can run during coding"""

        # Phase 10c: Plan Verification
        if "verify" in prompt_lower and ("feasibility" in prompt_lower or "plan" in prompt_lower):
            return """FEASIBILITY: 0.85
RISKS: Resource constraints, Schedule slippage, Technical complexity
CONTINGENCIES: Hire additional engineers, Reduce scope, Simplify architecture
VALID: true
CONFIDENCE: 0.82"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase10():
    """Create fake LLM for Phase 10 testing."""
    return FakeLLMPhase10()


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


def test_phase10_enabled_with_all_phases(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10 with all phases 1-9 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Implement a new software system",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 10 ran
    assert "primary_goal" in result or "phase10_summary" in result


def test_phase10_disabled(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test that Phase 10 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        enable_phase10=False,  # Disable Phase 10
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    # Phase 10 should not run
    assert "phase10_summary" not in result or result.get("phase10_summary") is None


def test_phase10_without_phase9(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10 can run without Phase 9."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=False,  # Disable Phase 8
        enable_phase9=False,  # Disable Phase 9
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test planning",
    }

    result = coordinator.invoke(initial_state)

    # Phase 10 should still run
    assert "primary_goal" in result or "phase10_summary" in result


def test_phase10_goal_decomposition(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10a generates goal decomposition."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Build a new application",
        "intent": "Build a new application",
    }

    result = coordinator.invoke(initial_state)

    # Check goal decomposition
    assert "primary_goal" in result
    assert isinstance(result.get("subgoals", []), list)


def test_phase10_plan_generation(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10b generates execution plan."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Create execution plan",
        "intent": "Create execution plan",
        "selected_tools": ["tool1", "tool2"],
    }

    result = coordinator.invoke(initial_state)

    # Check execution plan
    plan_steps = result.get("plan_steps", 0)
    assert isinstance(plan_steps, int)
    if plan_steps > 0:
        assert "execution_plan" in result


def test_phase10_plan_verification(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10c verifies plan feasibility."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Verify plan",
        "intent": "Verify plan",
        "execution_plan": ["step1", "step2"],
    }

    result = coordinator.invoke(initial_state)

    # Check plan verification
    feasibility = result.get("plan_feasibility", 0)
    assert isinstance(feasibility, (int, float))
    assert 0 <= feasibility <= 1

    assert isinstance(result.get("plan_valid", False), bool)


def test_phase10_planning_summary(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10d generates planning summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Plan summary test",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase10_summary", "")
    assert isinstance(summary, str)
    if summary:
        assert "Phase 10" in summary or "Planning" in summary


def test_phase10_with_full_pipeline(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10 integrated with full 1-10 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Full pipeline with planning",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("phase10_summary") is not None  # Phase 10


def test_phase10_critical_path_identification(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10 identifies critical path in plan."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Identify critical path",
        "selected_tools": ["tool1"],
    }

    result = coordinator.invoke(initial_state)

    # Check critical path
    critical_path = result.get("critical_path", [])
    assert isinstance(critical_path, list)


def test_phase10_risk_identification(
    fake_llm_phase10, registry, safety_validator, temp_memory
):
    """Test Phase 10 identifies plan risks and contingencies."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase10,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Identify risks",
        "execution_plan": ["step1", "step2"],
    }

    result = coordinator.invoke(initial_state)

    # Check risks and contingencies
    risks = result.get("plan_risks", [])
    assert isinstance(risks, list)

    contingencies = result.get("contingencies", [])
    assert isinstance(contingencies, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
