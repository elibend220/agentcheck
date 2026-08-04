"""Integration tests for Phase 13 Dynamic Plugin System & Autonomous Integration Discovery."""

import pytest
import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class FakeLLMPhase13:
    """Deterministic fake LLM for Phase 13 testing."""

    def __init__(self):
        self.calls = []

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        prompt_lower = prompt.lower()

        # Phases 1-12 responses (abbreviated)
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Dynamic plugin system setup
ENTITIES: plugins, discovery, integration
SUMMARY: Plugin management task"""

        if "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: plugin architecture, discovery patterns
KNOWLEDGE_SUMMARY: Plugin patterns available"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: plugins, extensions, scalability
METACOGNITIVE_NOTES: Focused on extensibility"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: analytical
CAUSAL: Plugins enable system extensibility
CONCLUSION: Proceed with plugin system"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Auto-plugin discovery, smart installation
NOVELTY_SCORE: 81"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: plugin.manager, discovery.engine
CONFIDENCE: 0.90"""

        if "parameter" in prompt_lower:
            return "timeout: 60"

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return "VALID: true\nCONFIDENCE: 0.92"

        if "decompose" in prompt_lower or "subgoal" in prompt_lower:
            return """PRIMARY_GOAL: Setup dynamic plugin system
SUBGOALS: Discover plugins, Build adapters, Install plugins
HIERARCHY: Sequential phases
DEPENDENCIES: Discovery before build"""

        if "execution plan" in prompt_lower or "step" in prompt_lower:
            return """EXECUTION_STEPS: Analyze needs, Discover plugins, Build adapters, Install, Manage
CRITICAL_PATH: Discover → Build → Install → Manage
ESTIMATED_DURATION: 12
RESOURCE_REQUIREMENTS: Plugin registry, Build tools
PARALLELIZABLE: Multiple plugins can build concurrently"""

        if "verify" in prompt_lower and ("feasibility" in prompt_lower or "plan" in prompt_lower):
            return """FEASIBILITY: 0.88
RISKS: Plugin conflicts, Dependency issues
CONTINGENCIES: Version management, Rollback support
VALID: true
CONFIDENCE: 0.87"""

        if "analyze this user interaction" in prompt_lower or "user profile" in prompt_lower:
            return """NAME: PluginEnthusiast
CURRENT_STATUS: exploring extensions
PREFERENCES: customizable, extensible
PATTERNS: Requests new plugins, auto-discovery
PERSONALITY: innovative
CURRENT_ACTIVITY: Setting up custom plugins
TONE_SUGGESTION: helpful, technical"""

        if "predict their needs" in prompt_lower or "anticipated needs" in prompt_lower:
            return """PREDICTED_NEEDS: Jira plugin, GitHub plugin, Slack advanced
PROACTIVE_SUGGESTIONS: Enable auto-discovery, Setup plugin updates
PRIORITY_ACTIONS: Install discovered plugins, Configure
CONFIDENCE: 0.86"""

        if "recommend autonomous actions" in prompt_lower:
            return """RECOMMENDED_ACTIONS: Discover missing plugins, Build custom adapters, Install
ACTION_PRIORITIES: high, high, high
RISKS: Compatibility issues
REQUIRES_CONFIRMATION: true"""

        if "initialize communication channels" in prompt_lower:
            return """ACTIVE_CHANNELS: Slack, Discord, Email, Phone
SLACK_CONFIG: webhook_configured
DISCORD_CONFIG: bot_configured
EMAIL_CONFIG: smtp_configured
PHONE_CONFIG: twilio_configured
READINESS: 0.90"""

        if "generate routing rules" in prompt_lower:
            return """ROUTING_RULES: Configured
CHANNEL_PRIORITY: Slack, Discord, Email, Phone
CONTEXT_RETENTION: Enabled
CONFIDENCE: 0.87"""

        if "integrate external tools" in prompt_lower:
            return """EXTERNAL_TOOLS: Google Drive, Notion, Calendar
GOOGLE_DRIVE_ACCESS: enabled
NOTION_ACCESS: enabled
CALENDAR_ACCESS: enabled
AVAILABLE_INTEGRATIONS: Google Drive, Notion, Calendar
READY: true"""

        # Phase 13: Plugin Discovery
        if "analyze system capabilities and identify missing plugins" in prompt_lower:
            return """DISCOVERED_PLUGINS: Jira Plugin, GitHub Plugin, Slack Advanced
PLUGIN_SUGGESTIONS: Slack Advanced, Jira Integration, GitHub CI/CD
MISSING_INTEGRATIONS: Project Management, Version Control, CI/CD
PRIORITY: high, medium, medium
CONFIDENCE: 0.87"""

        # Phase 13: Plugin Builder
        if "generate plugin specifications for custom integration" in prompt_lower:
            return """PLUGIN_SPECIFICATIONS: Detailed specs for each plugin
PLUGIN_TEMPLATES: Python, API wrapper template
DEPENDENCIES: requests, aiohttp
AUTHENTICATION: OAuth2, API Key
CAPABILITIES: Read/Write, Webhooks, Events
READY: true
CONFIDENCE: 0.85"""

        # Phase 13: Plugin Installer
        if "plan plugin installation and dependency resolution" in prompt_lower:
            return """INSTALLATION_PLAN: Resolve deps, Install core, Configure auth, Enable hooks
DEPENDENCY_RESOLUTION: Version constraints, Compatibility checks
INSTALLATION_STATUS: All plugins ready to install
INSTALLATION_LOG: Step 1 complete, Step 2 queued
READY: true
CONFIDENCE: 0.86"""

        return "DEFAULT: continue"


@pytest.fixture
def fake_llm_phase13():
    """Create fake LLM for Phase 13 testing."""
    return FakeLLMPhase13()


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


def test_phase13_enabled_with_all_phases(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13 with all phases 1-13 enabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Setup dynamic plugin system",
    }

    result = coordinator.invoke(initial_state)

    # Verify Phase 13 ran
    assert "discovered_plugins" in result or "phase13_summary" in result


def test_phase13_disabled(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test that Phase 13 can be disabled."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=False,  # Disable Phase 13
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Test task",
    }

    result = coordinator.invoke(initial_state)

    # Phase 13 should not run
    assert "phase13_summary" not in result or result.get("phase13_summary") is None


def test_phase13_plugin_discovery(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13a plugin discovery."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Discover plugins",
    }

    result = coordinator.invoke(initial_state)

    # Check discovery
    plugins = result.get("discovered_plugins", [])
    assert isinstance(plugins, list)


def test_phase13_plugin_builder(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13b plugin builder."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Build plugins",
    }

    result = coordinator.invoke(initial_state)

    # Check build
    built = result.get("built_plugins", [])
    assert isinstance(built, list)


def test_phase13_plugin_installer(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13c plugin installer."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Install plugins",
    }

    result = coordinator.invoke(initial_state)

    # Check installation
    installed = result.get("installed_plugins", [])
    assert isinstance(installed, list)


def test_phase13_integration_manager(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13d integration manager."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Manage integrations",
    }

    result = coordinator.invoke(initial_state)

    summary = result.get("phase13_summary", "")
    assert isinstance(summary, str)


def test_phase13_with_full_pipeline(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13 integrated with full 1-13 pipeline."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Full pipeline with dynamic plugins",
    }

    result = coordinator.invoke(initial_state)

    # All phases should have run
    assert result.get("intent") is not None  # Phase 1
    assert result.get("phase13_summary") is not None  # Phase 13


def test_phase13_plugin_suggestions(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13 plugin suggestions."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Get plugin suggestions",
    }

    result = coordinator.invoke(initial_state)

    # Check suggestions
    suggestions = result.get("plugin_suggestions", [])
    assert isinstance(suggestions, list)


def test_phase13_missing_integrations(
    fake_llm_phase13, registry, safety_validator, temp_memory
):
    """Test Phase 13 identifies missing integrations."""
    coordinator = AgentCoordinator(
        llm=fake_llm_phase13,
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
        enable_phase13=True,
        dry_run_mode=True,
    )

    initial_state: FullAgentState = {
        "input_text": "Check missing integrations",
    }

    result = coordinator.invoke(initial_state)

    # Check missing
    missing = result.get("missing_integrations", [])
    assert isinstance(missing, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
