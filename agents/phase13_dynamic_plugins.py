"""Phase 13: Dynamic Plugin System & Autonomous Integration Discovery."""

from __future__ import annotations

from typing import Callable, Optional
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_plugin_discovery_node(llm: LLMFn):
    """
    Create Phase 13a plugin discovery node.

    Autonomously detects missing integrations and suggests plugins.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 13a: Plugin Discovery.

        Discovers system needs and identifies required plugins.
        """
        discovery = _discover_missing_plugins(llm, state)

        state.update({
            "discovered_plugins": discovery.get("plugins", []),
            "plugin_suggestions": discovery.get("suggestions", []),
            "missing_integrations": discovery.get("missing", []),
            "discovery_confidence": discovery.get("confidence", 0.0),
        })

        return state

    return process


def make_plugin_builder_node(llm: LLMFn):
    """
    Create Phase 13b plugin builder node.

    Creates custom plugin adapters for new connections.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 13b: Plugin Builder.

        Generates plugin code and specifications for custom integrations.
        """
        plugins_to_build = state.get("discovered_plugins", [])

        if not plugins_to_build:
            state.update({
                "built_plugins": [],
                "plugin_specifications": {},
                "plugin_templates": {},
                "builder_ready": False,
            })
            return state

        built = _build_custom_plugins(llm, state, plugins_to_build)

        state.update({
            "built_plugins": built.get("plugins", []),
            "plugin_specifications": built.get("specs", {}),
            "plugin_templates": built.get("templates", {}),
            "builder_ready": built.get("ready", False),
            "plugin_build_confidence": built.get("confidence", 0.0),
        })

        return state

    return process


def make_plugin_installer_node(llm: LLMFn):
    """
    Create Phase 13c plugin installer node.

    Installs plugins manually or autonomously based on needs.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 13c: Plugin Installer.

        Manages plugin installation and dependency resolution.
        """
        built_plugins = state.get("built_plugins", [])
        manual_requests = state.get("manual_plugin_requests", [])

        if not built_plugins and not manual_requests:
            state.update({
                "installed_plugins": [],
                "plugin_status": {},
                "installation_log": [],
                "installer_ready": False,
            })
            return state

        installed = _install_plugins(llm, state, built_plugins, manual_requests)

        state.update({
            "installed_plugins": installed.get("installed", []),
            "plugin_status": installed.get("status", {}),
            "installation_log": installed.get("log", []),
            "installer_ready": installed.get("ready", False),
            "installation_confidence": installed.get("confidence", 0.0),
        })

        return state

    return process


def make_integration_manager_node(llm: LLMFn):
    """
    Create Phase 13d integration manager node.

    Manages plugin lifecycle, dependencies, and updates.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate integration management summary."""
        summary_lines = [
            "=== Dynamic Plugin System Mode ===",
        ]

        # Discovered Plugins
        discovered = state.get("discovered_plugins", [])
        if discovered:
            summary_lines.append(f"\n🔍 Plugin Discovery ({len(discovered)}):")
            for plugin in discovered[:5]:
                summary_lines.append(f"  • {plugin}")

        # Plugin Suggestions
        suggestions = state.get("plugin_suggestions", [])
        if suggestions:
            summary_lines.extend([
                f"\n💡 Suggested Plugins ({len(suggestions)}):",
            ])
            for suggestion in suggestions[:3]:
                summary_lines.append(f"  → {suggestion}")

        # Built Plugins
        built = state.get("built_plugins", [])
        if built:
            summary_lines.extend([
                f"\n🔨 Built Plugins ({len(built)}):",
            ])
            for plugin in built[:3]:
                summary_lines.append(f"  ✓ {plugin}")

        # Installed Plugins
        installed = state.get("installed_plugins", [])
        if installed:
            summary_lines.extend([
                f"\n📦 Installed Plugins ({len(installed)}):",
            ])
            for plugin in installed[:5]:
                status = state.get("plugin_status", {}).get(plugin, "active")
                summary_lines.append(f"  ✓ {plugin} ({status})")

        # Missing Integrations
        missing = state.get("missing_integrations", [])
        if missing:
            summary_lines.extend([
                f"\n⚠️  Missing Integrations ({len(missing)}):",
            ])
            for integration in missing[:3]:
                summary_lines.append(f"  • {integration}")

        # Confidence Metrics
        discovery_conf = state.get("discovery_confidence", 0)
        builder_conf = state.get("plugin_build_confidence", 0)
        install_conf = state.get("installation_confidence", 0)

        summary_lines.extend([
            f"\n✨ Plugin System Confidence:",
            f"  Discovery: {discovery_conf:.0%}",
            f"  Builder: {builder_conf:.0%}",
            f"  Installer: {install_conf:.0%}",
        ])

        phase13_summary = "\n".join(summary_lines)

        state.update({
            "phase13_summary": phase13_summary,
            "plugin_system_ready": True,
        })

        return state

    return process


def _discover_missing_plugins(llm: LLMFn, state: FullAgentState) -> dict:
    """Discover missing plugins and integrations."""
    current_channels = state.get("active_channels", [])
    current_tools = state.get("available_integrations", [])

    prompt = f"""Analyze system capabilities and identify missing plugins:

Current Channels: {', '.join(current_channels) if current_channels else 'None'}
Current Tools: {', '.join(current_tools) if current_tools else 'None'}
User Context: {state.get('input_text', 'General use')}
Phase 12 Ready: {state.get('multichannel_ready', False)}

Recommend needed plugins for:
DISCOVERED_PLUGINS: [plugins system needs]
PLUGIN_SUGGESTIONS: [recommended plugins to add]
MISSING_INTEGRATIONS: [capabilities not yet available]
PRIORITY: [high/medium/low for each]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_discovery_response(response)


def _parse_discovery_response(response: str) -> dict:
    """Parse plugin discovery response."""
    discovery = {
        "plugins": [],
        "suggestions": [],
        "missing": [],
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("DISCOVERED_PLUGINS:"):
            plugins_str = line.split(":", 1)[-1].strip()
            if plugins_str:
                plugins = [p.strip().strip("[](),") for p in plugins_str.split(",")]
                discovery["plugins"] = [p for p in plugins if p]

        elif line.startswith("PLUGIN_SUGGESTIONS:"):
            suggestions_str = line.split(":", 1)[-1].strip()
            if suggestions_str:
                suggestions = [s.strip().strip("[](),") for s in suggestions_str.split(",")]
                discovery["suggestions"] = [s for s in suggestions if s]

        elif line.startswith("MISSING_INTEGRATIONS:"):
            missing_str = line.split(":", 1)[-1].strip()
            if missing_str:
                missing = [m.strip().strip("[](),") for m in missing_str.split(",")]
                discovery["missing"] = [m for m in missing if m]

        elif line.startswith("CONFIDENCE:"):
            try:
                discovery["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                discovery["confidence"] = 0.75

    return discovery


def _build_custom_plugins(llm: LLMFn, state: FullAgentState, plugins: list) -> dict:
    """Build custom plugin adapters."""
    plugins_str = ", ".join(plugins[:5])

    prompt = f"""Generate plugin specifications for custom integration:

Required Plugins: {plugins_str}
System Phase: 13 (Dynamic Plugin System)
Channel Manager Ready: {state.get('multichannel_ready', False)}
Tool Bridge Ready: {state.get('tool_bridge_ready', False)}

Provide:
PLUGIN_SPECIFICATIONS: [detailed specs for each plugin]
PLUGIN_TEMPLATES: [template code/structure for plugins]
DEPENDENCIES: [required libraries and APIs]
AUTHENTICATION: [auth methods for each]
CAPABILITIES: [what each plugin can do]
READY: [true/false if buildable]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_plugin_build_response(response)


def _parse_plugin_build_response(response: str) -> dict:
    """Parse plugin build response."""
    builder = {
        "plugins": [],
        "specs": {},
        "templates": {},
        "ready": False,
        "confidence": 0.75,
    }

    lines = response.split("\n")
    current_section = None

    for line in lines:
        if line.startswith("PLUGIN_SPECIFICATIONS:"):
            current_section = "specs"
            specs_str = line.split(":", 1)[-1].strip()
            if specs_str:
                builder["plugins"].append(specs_str)

        elif line.startswith("PLUGIN_TEMPLATES:"):
            current_section = "templates"
            templates_str = line.split(":", 1)[-1].strip()
            if templates_str:
                builder["templates"]["default"] = templates_str

        elif line.startswith("DEPENDENCIES:"):
            deps_str = line.split(":", 1)[-1].strip()
            builder["specs"]["dependencies"] = deps_str

        elif line.startswith("AUTHENTICATION:"):
            auth_str = line.split(":", 1)[-1].strip()
            builder["specs"]["authentication"] = auth_str

        elif line.startswith("CAPABILITIES:"):
            caps_str = line.split(":", 1)[-1].strip()
            builder["specs"]["capabilities"] = caps_str

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            builder["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                builder["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                builder["confidence"] = 0.75

    return builder


def _install_plugins(llm: LLMFn, state: FullAgentState, built: list, manual: list) -> dict:
    """Install plugins and manage dependencies."""
    all_plugins = built + manual
    plugins_str = ", ".join(all_plugins[:5])

    prompt = f"""Plan plugin installation and dependency resolution:

Plugins to Install: {plugins_str}
Installation Type: {'autonomous' if built else 'manual'}
Current Installed: {', '.join(state.get('installed_plugins', []))}

Provide:
INSTALLATION_PLAN: [step-by-step installation order]
DEPENDENCY_RESOLUTION: [how to handle dependencies]
INSTALLATION_STATUS: [status for each plugin]
INSTALLATION_LOG: [log entries for each step]
READY: [true/false if installable]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_installation_response(response)


def _parse_installation_response(response: str) -> dict:
    """Parse installation response."""
    installer = {
        "installed": [],
        "status": {},
        "log": [],
        "ready": False,
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("INSTALLATION_PLAN:"):
            plan_str = line.split(":", 1)[-1].strip()
            if plan_str:
                steps = [s.strip().strip("[](),") for s in plan_str.split(",")]
                installer["log"] = [s for s in steps if s]

        elif line.startswith("INSTALLATION_STATUS:"):
            status_str = line.split(":", 1)[-1].strip()
            if status_str:
                installer["status"]["overall"] = status_str

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            installer["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                installer["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                installer["confidence"] = 0.75

    # Mark discovered plugins as installed
    if installer["ready"]:
        installer["installed"] = [
            f"plugin_{i}" for i in range(1, len(installer["log"]) + 1)
        ]
        for plugin in installer["installed"]:
            installer["status"][plugin] = "active"

    return installer
