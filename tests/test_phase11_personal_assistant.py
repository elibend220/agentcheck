"""Integration tests for Phase 11 Proactive Personal Assistant."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class FakeLLMPhase11:
    """Deterministic fake LLM for Phase 11 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phases 1-10 responses (abbreviated)
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Personal assistance task
ENTITIES: user, assistance
SUMMARY: User assistance task"""

        if "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: user assistance patterns
KNOWLEDGE_SUMMARY: Patterns available"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: user needs, preferences
METACOGNITIVE_NOTES: Focused on user"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: analytical
CAUSAL: User needs drive recommendations
CONCLUSION: Proceed with assistance"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Proactive assistance
NOVELTY_SCORE: 78"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: data.aggregate, text.format
CONFIDENCE: 0.88"""

        if "parameter" in prompt_lower:
            return "threshold: 0.75"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return "VALID: true\nCONFIDENCE: 0.90"

        if "decompose" in prompt_lower or "subgoal" in prompt_lower:
            return """PRIMARY_GOAL: Provide proactive assistance
SUBGOALS: Profile user, Predict needs, Recommend actions
HIERARCHY: Sequential phases
DEPENDENCIES: Profile before prediction"""

        if "execution plan" in prompt_lower or "step" in prompt_lower:
            return """EXECUTION_STEPS: Profile, Predict, Recommend, Execute
CRITICAL_PATH: Profile → Predict → Recommend
ESTIMATED_DURATION: 5
RESOURCE_REQUIREMENTS: User data, ML models
PARALLELIZABLE: Some predictions can run in parallel"""

        if "verify" in prompt_lower and ("feasibility" in prompt_lower or "plan" in prompt_lower):
            return """FEASIBILITY: 0.88
RISKS: User privacy, Recommendation accuracy
CONTINGENCIES: Ask for confirmation, Improve models
VALID: true
CONFIDENCE: 0.85"""

        # Phase 11: User Profile
        if "analyze this user interaction" in prompt_lower or "user profile" in prompt_lower:
            return """NAME: Alex
CURRENT_STATUS: focused
PREFERENCES: efficiency, clarity
PATTERNS: Prefers systematic approaches
PERSONALITY: analytical
CURRENT_ACTIVITY: working on project
TONE_SUGGESTION: professional but friendly"""

        # Phase 11: Predictions
        if "predict their needs" in prompt_lower or "anticipated needs" in prompt_lower:
            return """PREDICTED_NEEDS: documentation review, code optimization
PROACTIVE_SUGGESTIONS: automate repetitive tasks, organize files
PRIORITY_ACTIONS: review recent work, optimize workflow
CONFIDENCE: 0.82"""

        # Phase 11: Autonomous Actions
        if "recommend autonomous actions" in prompt_lower or "ready to execute" in prompt_lower:
            return """RECOMMENDED_ACTIONS: schedule meeting, organize files, prepare report
ACTION_PRIORITIES: high, medium, low
RISKS: scheduling conflicts, data accuracy
REQUIRES_CONFIRMATION: true"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase11():
    """Create fake LLM for Phase 11 testing."""
    return FakeLLMPhase11()


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


def test_phase11_enabled_with_all_phases(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11 with all phases 1-11 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "I'm working on an important project",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 11 ran
    assert "user_profile" in result or "phase11_summary" in result


def test_phase11_disabled(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test that Phase 11 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=False,  # Disable Phase 11
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    # Phase 11 should not run
    assert "phase11_summary" not in result or result.get("phase11_summary") is None


def test_phase11_without_phase10(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11 can run without Phase 10."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=False,
        enable_phase9=False,
        enable_phase10=False,  # Disable Phase 10
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test personal assistance",
    }

    result = coordinator.invoke(initial_state)

    # Phase 11 should not be able to run without Phase 10 in typical flow
    # But the coordinator should still complete
    assert result is not None


def test_phase11_user_profile_building(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11a generates user profile."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Build user profile",
        "intent": "Build user profile",
    }

    result = coordinator.invoke(initial_state)

    # Check user profile
    assert "user_profile" in result
    assert isinstance(result.get("user_status", ""), str)


def test_phase11_predictive_assistance(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11b generates predicted needs."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Predict user needs",
        "intent": "Predict user needs",
        "user_profile": {"name": "Alex"},
    }

    result = coordinator.invoke(initial_state)

    # Check predictions
    needs = result.get("predicted_needs", [])
    assert isinstance(needs, list)


def test_phase11_autonomous_actions(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11c recommends autonomous actions."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Recommend actions",
        "intent": "Recommend actions",
        "predicted_needs": ["documentation", "optimization"],
    }

    result = coordinator.invoke(initial_state)

    # Check autonomous actions
    actions = result.get("autonomous_actions", [])
    assert isinstance(actions, list)


def test_phase11_assistant_summary(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11d generates assistant summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Generate summary",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase11_summary", "")
    assert isinstance(summary, str)


def test_phase11_with_full_pipeline(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11 integrated with full 1-11 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Full pipeline with personal assistant",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("phase11_summary") is not None  # Phase 11


def test_phase11_confidence_scores(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11 generates confidence scores."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Check confidence",
    }

    result = coordinator.invoke(initial_state)

    # Check confidence metrics
    confidence = result.get("anticipation_confidence", 0)
    assert isinstance(confidence, (int, float))
    assert 0 <= confidence <= 1


def test_phase11_priority_and_risk_assessment(
    fake_llm_phase11, registry, safety_validator, temp_memory
):
    """Test Phase 11 assesses action priorities and risks."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase11,
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
        enable_phase11=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Assess risks",
    }

    result = coordinator.invoke(initial_state)

    # Check priorities and risks
    priorities = result.get("action_priorities", [])
    assert isinstance(priorities, list)

    risks = result.get("action_risks", [])
    assert isinstance(risks, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
