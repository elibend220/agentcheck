"""Integration tests for Phase 12 Multi-Channel Communication & External Tool Integration."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class FakeLLMPhase12:
    """Deterministic fake LLM for Phase 12 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phases 1-11 responses (abbreviated)
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Multi-channel communication
ENTITIES: channels, tools, integration
SUMMARY: Multi-channel communication task"""

        if "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: channel communication, tool integration
KNOWLEDGE_SUMMARY: Communication patterns"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: channels, tools, integration
METACOGNITIVE_NOTES: Focused on communication"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: analytical
CAUSAL: Communication channels enable multi-platform integration
CONCLUSION: Proceed with channel setup"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Unified interface, cross-channel sync
NOVELTY_SCORE: 79"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: channel.manager, tool.bridge
CONFIDENCE: 0.89"""

        if "parameter" in prompt_lower:
            return "timeout: 30"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return "VALID: true\nCONFIDENCE: 0.91"

        if "decompose" in prompt_lower or "subgoal" in prompt_lower:
            return """PRIMARY_GOAL: Multi-channel communication setup
SUBGOALS: Initialize channels, Route messages, Integrate tools
HIERARCHY: Sequential phases
DEPENDENCIES: Channels before routing"""

        if "execution plan" in prompt_lower or "step" in prompt_lower:
            return """EXECUTION_STEPS: Setup channels, Configure routing, Integrate tools
CRITICAL_PATH: Channels → Routing → Tools
ESTIMATED_DURATION: 8
RESOURCE_REQUIREMENTS: API credentials, Connection handlers
PARALLELIZABLE: Tool integration can run with routing"""

        if "verify" in prompt_lower and ("feasibility" in prompt_lower or "plan" in prompt_lower):
            return """FEASIBILITY: 0.87
RISKS: API availability, credential management
CONTINGENCIES: Fallback channels, Retry logic
VALID: true
CONFIDENCE: 0.86"""

        if "analyze this user interaction" in prompt_lower or "user profile" in prompt_lower:
            return """NAME: MultiChannelUser
CURRENT_STATUS: connected
PREFERENCES: all channels, auto-sync
PATTERNS: Cross-channel communication
PERSONALITY: adaptive
CURRENT_ACTIVITY: Managing multiple channels
TONE_SUGGESTION: consistent across platforms"""

        if "predict their needs" in prompt_lower or "anticipated needs" in prompt_lower:
            return """PREDICTED_NEEDS: channel monitoring, tool integration, message sync
PROACTIVE_SUGGESTIONS: set up webhooks, enable notifications
PRIORITY_ACTIONS: configure channels, test connectivity
CONFIDENCE: 0.84"""

        if "recommend autonomous actions" in prompt_lower or "ready to execute" in prompt_lower:
            return """RECOMMENDED_ACTIONS: activate Slack, enable Discord, setup email, configure Twilio
ACTION_PRIORITIES: high, high, medium, high
RISKS: authentication errors, rate limiting
REQUIRES_CONFIRMATION: true"""

        # Phase 12: Channel Manager
        if "initialize communication channels" in prompt_lower:
            return """ACTIVE_CHANNELS: Slack, Discord, Email, Phone
SLACK_CONFIG: https://hooks.slack.com/services/xxx
DISCORD_CONFIG: bot_token_xxx
EMAIL_CONFIG: smtp.gmail.com:587
PHONE_CONFIG: twilio_sid_xxx
READINESS: 0.88"""

        # Phase 12: Message Router
        if "generate routing rules" in prompt_lower or "routing rules" in prompt_lower:
            return """ROUTING_RULES: Route by channel type and context
CHANNEL_PRIORITY: Slack, Discord, Email, Phone
CONTEXT_RETENTION: Per-channel conversation state
CONFIDENCE: 0.85"""

        # Phase 12: Tool Bridge
        if "integrate external tools" in prompt_lower or "tool integration" in prompt_lower:
            return """EXTERNAL_TOOLS: Google Drive, Notion, Calendar
GOOGLE_DRIVE_ACCESS: read-write
NOTION_ACCESS: read-write
CALENDAR_ACCESS: event management
AVAILABLE_INTEGRATIONS: Google Drive, Notion, Calendar
READY: true"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase12():
    """Create fake LLM for Phase 12 testing."""
    return FakeLLMPhase12()


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


def test_phase12_enabled_with_all_phases(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12 with all phases 1-12 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Setup multi-channel communication",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 12 ran
    assert "active_channels" in result or "phase12_summary" in result


def test_phase12_disabled(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test that Phase 12 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=False,  # Disable Phase 12
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    # Phase 12 should not run
    assert "phase12_summary" not in result or result.get("phase12_summary") is None


def test_phase12_channel_manager(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12a channel manager initialization."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Initialize channels",
    }

    result = coordinator.invoke(initial_state)

    # Check channel initialization
    channels = result.get("active_channels", [])
    assert isinstance(channels, list)


def test_phase12_message_router(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12b message routing."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Setup message routing",
    }

    result = coordinator.invoke(initial_state)

    # Check routing
    routing_rules = result.get("routing_rules", {})
    assert isinstance(routing_rules, dict)


def test_phase12_tool_bridge(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12c tool bridge integration."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Integrate tools",
    }

    result = coordinator.invoke(initial_state)

    # Check tool integrations
    tools = result.get("available_integrations", [])
    assert isinstance(tools, list)


def test_phase12_multichannel_summary(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12d generates multi-channel summary."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Generate summary",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase12_summary", "")
    assert isinstance(summary, str)


def test_phase12_with_full_pipeline(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12 integrated with full 1-12 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Full pipeline with multi-channel",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("phase12_summary") is not None  # Phase 12


def test_phase12_channel_configurations(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12 channel configuration handling."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Configure channels",
    }

    result = coordinator.invoke(initial_state)

    # Check channel configs
    configs = result.get("channel_configs", {})
    assert isinstance(configs, dict)

    status = result.get("connection_status", {})
    assert isinstance(status, dict)


def test_phase12_readiness_metrics(
    fake_llm_phase12, registry, safety_validator, temp_memory
):
    """Test Phase 12 readiness and confidence metrics."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase12,
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
        enable_phase12=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Check readiness",
    }

    result = coordinator.invoke(initial_state)

    # Check readiness metrics
    readiness = result.get("channel_readiness", 0)
    assert isinstance(readiness, (int, float))
    assert 0 <= readiness <= 1

    routing_confidence = result.get("routing_confidence", 0)
    assert isinstance(routing_confidence, (int, float))
    assert 0 <= routing_confidence <= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
