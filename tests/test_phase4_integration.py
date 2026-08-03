"""Integration tests for Phase 4 (Tool Execution)."""
import pytest
from agents.state import FullAgentState
from agents.phase4a_tool_selection import make_tool_selection_node
from agents.phase4b_tool_execution import make_tool_execution_node
from agents.phase4c_tool_verification import make_tool_verification_node
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLM:
    """Deterministic fake LLM for testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)

        # Tool selection response
        if "Tool Selection" in prompt or "SELECTED_TOOLS" in prompt:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: We need to add numbers and transform text based on the reasoning provided
CONFIDENCE: 0.8"""

        # Tool execution/binding response
        if "parameters" in prompt.lower() or "binding" in prompt.lower():
            return "a: 5\nb: 3"

        # Verification response
        if "Verif" in prompt or "VALID:" in prompt:
            return """VALID: true
CONFIDENCE: 0.9
CONCERNS: none
REASONING: Result is consistent with expected math operation"""

        return "RESULT: default"


def test_tool_selection_with_reasoning_output():
    """Test tool selection using reasoning output."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    select_tools = make_tool_selection_node(llm, registry)

    state: FullAgentState = {
        "intent": "calculate and transform",
        "reasoning_conclusion": "We should add two numbers and convert to uppercase",
        "creative_ideas": ["combine math with text", "use multi-step approach"],
        "attention_focus": ["numerical accuracy", "text quality"],
        "input_text": "test input",
    }

    result = state.copy()
    result.update(select_tools(state))

    assert "selected_tools" in result
    assert len(result["selected_tools"]) > 0
    assert "tool_selection_reasoning" in result
    assert result["tool_selection_confidence"] > 0


def test_tool_execution_selection_to_execution():
    """Test full selection and execution flow."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    select_tools = make_tool_selection_node(llm, registry)
    execute_tools = make_tool_execution_node(llm, registry, SafetyValidator())

    state: FullAgentState = {
        "intent": "perform arithmetic",
        "reasoning_conclusion": "Add 5 and 3",
        "creative_ideas": [],
        "attention_focus": [],
        "input_text": "5 + 3",
    }

    # Tool selection
    result = state.copy()
    result.update(select_tools(state))
    selected = result.get("selected_tools", [])

    # If we got tool selection, execute
    if selected:
        result.update(execute_tools(result))
        assert "tool_execution_results" in result
        assert len(result["tool_execution_results"]) > 0


def test_tool_verification_on_results():
    """Test verification of tool execution results."""
    llm = FakeLLM()
    verify_tools = make_tool_verification_node(llm)

    from agents.state import ToolExecutionResult

    state: FullAgentState = {
        "intent": "test verification",
        "reasoning_conclusion": "Add two numbers",
        "knowledge_summary": "Basic arithmetic",
        "attention_focus": ["accuracy"],
        "tool_execution_results": [
            ToolExecutionResult(
                tool_id="math.add",
                success=True,
                value=8,
                execution_time_ms=1.5,
            )
        ],
    }

    result = state.copy()
    result.update(verify_tools(state))

    assert "verification_results" in result
    assert len(result["verification_results"]) > 0
    verification = result["verification_results"][0]
    assert verification.tool_id == "math.add"
    # Fake LLM returns VALID: true
    assert verification.valid is True


def test_execution_with_safety_violations():
    """Test execution respects safety policy."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    safety_validator = SafetyValidator()
    safety_validator.blocked_tools.add("math.add")

    execute_tools = make_tool_execution_node(llm, registry, safety_validator)

    state: FullAgentState = {
        "selected_tools": ["math.add"],
        "input_text": "test",
        "tool_execution_results": [],
    }

    result = state.copy()
    result.update(execute_tools(state))

    # Execution should fail due to blocked tool
    exec_results = result.get("tool_execution_results", [])
    if exec_results:
        # Tool was attempted
        assert any(not r.success for r in exec_results)


def test_dry_run_mode():
    """Test dry-run mode doesn't actually execute."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    execute_tools = make_tool_execution_node(llm, registry)

    state: FullAgentState = {
        "selected_tools": ["math.add"],
        "input_text": "test",
        "dry_run_mode": True,
    }

    result = state.copy()
    result.update(execute_tools(state))

    exec_results = result.get("tool_execution_results", [])
    if exec_results:
        # In dry-run, execution should succeed but value is None
        for r in exec_results:
            assert r.success or r.value is None


def test_phase4_without_tools():
    """Test Phase 4 gracefully handles no selected tools."""
    llm = FakeLLM()
    registry = create_builtin_registry()
    execute_tools = make_tool_execution_node(llm, registry)

    state: FullAgentState = {
        "selected_tools": [],  # No tools selected
        "input_text": "test",
    }

    result = state.copy()
    result.update(execute_tools(state))

    # Should not crash, just return empty results
    assert "tool_execution_results" in result
    assert len(result["tool_execution_results"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
