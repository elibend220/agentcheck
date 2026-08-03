"""Integration tests for Phase 7 Persistent Memory & Knowledge Integration."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager, ExecutionMemory


class FakeLLMPhase7:
    """Deterministic fake LLM for Phase 7 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phase 1-6 responses
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

        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool selection was effective
LESSON 2: Execution flowed smoothly
LESSON 3: Verification confirmed correctness"""

        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Consider using more diverse tools
SUGGESTION 2: Add more reasoning steps
SUGGESTION 3: Enhance creativity phase"""

        # Phase 7: Memory synthesis responses
        if "similar" in prompt_lower and "past" in prompt_lower:
            return """INSIGHT 1: Similar tasks use math.add effectively
INSIGHT 2: Verification phase important for this type
INSIGHT 3: Sequential execution works well
CONFIDENCE: 0.85
RECOMMENDED_APPROACH: Use math.add followed by text transformation"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase7():
    """Create fake LLM for Phase 7 testing."""
    return FakeLLMPhase7()


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
    """Create temporary memory manager for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    memory = MemoryManager(temp_path)
    yield memory
    # Cleanup
    import os
    if os.path.exists(temp_path):
        os.remove(temp_path)


def test_memory_manager_save_and_load(temp_memory):
    """Test memory manager can save and load memories."""
    memory = ExecutionMemory(
        input_text="Add 10 and 5",
        execution_outcome="success",
        lessons_learned=["Tools work well together"],
        tool_performance_scores={"math.add": 0.95},
        effective_tools=["math.add"],
        improvement_suggestions=["Continue this approach"],
        learning_metrics={"overall_learning_score": 0.9},
    )

    temp_memory.add_memory(memory)
    assert temp_memory.get_memory_size() == 1

    # Create new manager to test loading
    new_memory = MemoryManager(temp_memory.memory_file)
    assert new_memory.get_memory_size() == 1
    assert new_memory.memories[0].input_text == "Add 10 and 5"


def test_memory_manager_find_similar(temp_memory):
    """Test finding similar past executions."""
    # Add some memories
    temp_memory.add_memory(ExecutionMemory(
        input_text="Add two numbers together",
        execution_outcome="success",
        lessons_learned=["Math works"],
        tool_performance_scores={"math.add": 0.9},
        effective_tools=["math.add"],
        improvement_suggestions=[],
        learning_metrics={},
    ))

    temp_memory.add_memory(ExecutionMemory(
        input_text="Transform text to uppercase",
        execution_outcome="success",
        lessons_learned=["Text works"],
        tool_performance_scores={"text.uppercase": 0.95},
        effective_tools=["text.uppercase"],
        improvement_suggestions=[],
        learning_metrics={},
    ))

    # Find similar to first
    similar = temp_memory.find_similar_executions("Add numbers", similarity_threshold=0.3)
    assert len(similar) >= 1
    assert similar[0][0].input_text == "Add two numbers together"


def test_memory_manager_best_combinations(temp_memory):
    """Test getting best tool combinations."""
    temp_memory.add_memory(ExecutionMemory(
        input_text="Add and format",
        execution_outcome="success",
        lessons_learned=[],
        tool_performance_scores={"math.add": 0.9, "text.uppercase": 0.85},
        effective_tools=["math.add", "text.uppercase"],
        improvement_suggestions=[],
        learning_metrics={},
    ))

    combos = temp_memory.get_best_tool_combinations(limit=5)
    assert len(combos) >= 1
    assert "math.add" in combos[0]["tools"] or "text.uppercase" in combos[0]["tools"]


def test_phase7_enabled_with_memory(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 is enabled and uses memory."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Add numbers",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 7 output
    assert "memory_persisted" in result
    assert result.get("memory_size") is not None
    assert "phase7_summary" in result


def test_phase7_disabled(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test that Phase 7 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=False,  # Disable Phase 7
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 7 should not run
    assert "memory_persisted" not in result or result.get("memory_persisted") is None


def test_phase7_without_phase6(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 can run without Phase 6."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=False,  # Disable Phase 6
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test",
    }

    result = coordinator.invoke(initial_state)

    # Phase 7 should still run
    assert "memory_persisted" in result or "phase7_summary" in result


def test_phase7_memory_persistence_saves_execution(
    fake_llm_phase7, registry, safety_validator, temp_memory
):
    """Test that Phase 7 saves execution to memory."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test execution",
    }

    result = coordinator.invoke(initial_state)

    # Check memory was saved
    assert result.get("memory_size", 0) > 0
    assert temp_memory.get_memory_size() == 1


def test_phase7_retrieves_historical_knowledge(
    fake_llm_phase7, registry, safety_validator, temp_memory
):
    """Test that Phase 7 retrieves and uses historical knowledge."""
    # Pre-populate memory with a similar execution
    temp_memory.add_memory(ExecutionMemory(
        input_text="Add numbers and transform",
        execution_outcome="success",
        lessons_learned=["Math first, then text works well"],
        tool_performance_scores={"math.add": 0.95, "text.uppercase": 0.9},
        effective_tools=["math.add", "text.uppercase"],
        improvement_suggestions=["Keep this pattern"],
        learning_metrics={"overall_learning_score": 0.93},
    ))

    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Add and transform numbers",
    }

    result = coordinator.invoke(initial_state)

    # Should have found similar executions
    assert result.get("similar_past_executions", 0) > 0
    assert len(result.get("historical_lessons", [])) > 0


def test_phase7_with_full_pipeline(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 integrated with full pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Complete pipeline test",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("execution_outcome") is not None  # Phase 6
    assert result.get("memory_persisted") is not None  # Phase 7


def test_phase7_statistics_generation(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 generates execution statistics."""
    # Pre-populate with some data
    for i in range(3):
        temp_memory.add_memory(ExecutionMemory(
            input_text=f"Task {i}",
            execution_outcome="success" if i < 2 else "partial",
            lessons_learned=["Test lesson"],
            tool_performance_scores={"math.add": 0.9},
            effective_tools=["math.add"],
            improvement_suggestions=[],
            learning_metrics={"overall_learning_score": 0.85},
        ))

    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "New task",
    }

    result = coordinator.invoke(initial_state)

    # Check statistics
    stats = result.get("execution_statistics", {})
    assert stats.get("total_executions", 0) > 0
    assert stats.get("success_rate", 0) >= 0.0


def test_phase7_summary_generation(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 generates comprehensive summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase7_summary", "")
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Phase 7" in summary or "Memory" in summary


def test_phase7_synthesis_retrieval(fake_llm_phase7, registry, safety_validator, temp_memory):
    """Test Phase 7 retrieval and synthesis of historical insights."""
    # Pre-populate with similar execution
    temp_memory.add_memory(ExecutionMemory(
        input_text="Add and uppercase",
        execution_outcome="success",
        lessons_learned=["Sequential execution works"],
        tool_performance_scores={"math.add": 0.95},
        effective_tools=["math.add", "text.uppercase"],
        improvement_suggestions=["Continue pattern"],
        learning_metrics={"overall_learning_score": 0.92},
    ))

    coordinator = AgentCoordinator(
        llm=fake_llm_phase7,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=temp_memory,
        enable_phase4=True,
        enable_phase5=False,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Add numbers and format text",
    }

    result = coordinator.invoke(initial_state)

    # Check synthesis was performed
    assert "phase7_synthesis" in result
    synthesis = result.get("phase7_synthesis", "")
    assert len(synthesis) > 0
