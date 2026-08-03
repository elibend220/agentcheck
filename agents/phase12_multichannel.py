"""Phase 12: Multi-Channel Communication & External Tool Integration."""

from __future__ import annotations

from typing import Callable, Optional
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_channel_manager_node(llm: LLMFn):
    """
    Create Phase 12a channel manager node.

    Manages connections to multiple communication channels.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 12a: Channel Manager.

        Initializes and manages active channel connections.
        """
        channels = _initialize_channels(llm, state)

        state.update({
            "active_channels": channels.get("active_channels", []),
            "channel_configs": channels.get("channel_configs", {}),
            "connection_status": channels.get("connection_status", {}),
            "channel_readiness": channels.get("readiness", 0.0),
        })

        return state

    return process


def make_message_router_node(llm: LLMFn):
    """
    Create Phase 12b message router node.

    Routes messages and conversations across communication channels.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 12b: Message Router.

        Routes incoming messages to appropriate handlers and maintains context.
        """
        active_channels = state.get("active_channels", [])

        if not active_channels:
            state.update({
                "message_queue": [],
                "routing_rules": {},
                "channel_contexts": {},
            })
            return state

        routing = _generate_routing_rules(llm, state, active_channels)

        state.update({
            "message_queue": routing.get("queue", []),
            "routing_rules": routing.get("rules", {}),
            "channel_contexts": routing.get("contexts", {}),
            "routing_confidence": routing.get("confidence", 0.0),
        })

        return state

    return process


def make_tool_bridge_node(llm: LLMFn):
    """
    Create Phase 12c tool bridge node.

    Integrates external tools: Google Drive, Notion, Calendar.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 12c: Tool Bridge.

        Establishes connections to external tools and services.
        """
        external_tools = _integrate_external_tools(llm, state)

        state.update({
            "external_tools": external_tools.get("tools", []),
            "tool_connections": external_tools.get("connections", {}),
            "available_integrations": external_tools.get("available", []),
            "tool_bridge_ready": external_tools.get("ready", False),
            "tool_capabilities": external_tools.get("capabilities", {}),
        })

        return state

    return process


def make_multichannel_summary_node(llm: LLMFn):
    """
    Create Phase 12d multi-channel summary node.

    Generates platform-specific response formatting.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate multi-channel formatted response."""
        summary_lines = [
            "=== Multi-Channel Communication Mode ===",
        ]

        # Active Channels
        channels = state.get("active_channels", [])
        if channels:
            summary_lines.append(f"\n📡 Active Channels ({len(channels)}):")
            for channel in channels[:5]:
                status = state.get("connection_status", {}).get(channel, "unknown")
                summary_lines.append(f"  ✓ {channel} ({status})")

        # External Tool Integrations
        tools = state.get("available_integrations", [])
        if tools:
            summary_lines.extend([
                f"\n🔧 Integrated Tools ({len(tools)}):",
            ])
            for tool in tools[:5]:
                summary_lines.append(f"  ✓ {tool}")

        # Message Routing Status
        queue_size = len(state.get("message_queue", []))
        if queue_size > 0:
            summary_lines.append(f"\n📨 Message Queue: {queue_size} pending messages")

        # Channel Contexts
        contexts = state.get("channel_contexts", {})
        if contexts:
            summary_lines.append(f"\n💬 Channel Contexts ({len(contexts)}):")
            for channel_name in list(contexts.keys())[:3]:
                summary_lines.append(f"  • {channel_name}: Active")

        # Tool Capabilities
        capabilities = state.get("tool_capabilities", {})
        if capabilities:
            summary_lines.append(f"\n⚙️  Tool Capabilities:")
            for tool_name, caps in list(capabilities.items())[:2]:
                cap_list = ", ".join(caps[:2]) if isinstance(caps, list) else str(caps)
                summary_lines.append(f"  • {tool_name}: {cap_list}")

        # Readiness
        readiness = max(
            state.get("channel_readiness", 0.0),
            state.get("routing_confidence", 0.0),
        )
        summary_lines.extend([
            f"\n✨ System Readiness: {readiness:.0%}",
        ])

        phase12_summary = "\n".join(summary_lines)

        state.update({
            "phase12_summary": phase12_summary,
            "multichannel_ready": True,
        })

        return state

    return process


def _initialize_channels(llm: LLMFn, state: FullAgentState) -> dict:
    """Initialize communication channels."""
    prompt = f"""Initialize communication channels for the AGI system:

Available Channels: Slack, Discord, Email, Phone (Twilio)
Current Context: {state.get('input_text', 'General initialization')}

Provide:
ACTIVE_CHANNELS: [list of channels to activate]
SLACK_CONFIG: [webhook URL if available]
DISCORD_CONFIG: [bot token if available]
EMAIL_CONFIG: [SMTP settings if available]
PHONE_CONFIG: [Twilio credentials if available]
READINESS: [0.0-1.0 confidence in channel setup]"""

    response = llm(prompt)
    return _parse_channel_config(response)


def _parse_channel_config(response: str) -> dict:
    """Parse channel configuration from LLM response."""
    config = {
        "active_channels": [],
        "channel_configs": {},
        "connection_status": {},
        "readiness": 0.7,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ACTIVE_CHANNELS:"):
            channels_str = line.split(":", 1)[-1].strip()
            if channels_str:
                # Parse list format
                channels = [c.strip().strip("[](),") for c in channels_str.split(",")]
                config["active_channels"] = [c for c in channels if c]

        elif line.startswith("SLACK_CONFIG:"):
            config["channel_configs"]["slack"] = line.split(":", 1)[-1].strip()
            if config["channel_configs"]["slack"]:
                config["connection_status"]["slack"] = "connected"

        elif line.startswith("DISCORD_CONFIG:"):
            config["channel_configs"]["discord"] = line.split(":", 1)[-1].strip()
            if config["channel_configs"]["discord"]:
                config["connection_status"]["discord"] = "connected"

        elif line.startswith("EMAIL_CONFIG:"):
            config["channel_configs"]["email"] = line.split(":", 1)[-1].strip()
            if config["channel_configs"]["email"]:
                config["connection_status"]["email"] = "connected"

        elif line.startswith("PHONE_CONFIG:"):
            config["channel_configs"]["phone"] = line.split(":", 1)[-1].strip()
            if config["channel_configs"]["phone"]:
                config["connection_status"]["phone"] = "connected"

        elif line.startswith("READINESS:"):
            try:
                config["readiness"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                config["readiness"] = 0.7

    return config


def _generate_routing_rules(llm: LLMFn, state: FullAgentState, channels: list) -> dict:
    """Generate message routing rules for channels."""
    channels_str = ", ".join(channels)

    prompt = f"""Generate routing rules for multi-channel communication:

Available Channels: {channels_str}
Phase 11 Assistant: {state.get('user_status', 'active')}
Message Queue Size: {len(state.get('message_queue', []))}

Provide:
ROUTING_RULES: [rules for routing messages]
CHANNEL_PRIORITY: [priority order for channels]
CONTEXT_RETENTION: [how to maintain context per channel]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_routing_rules(response)


def _parse_routing_rules(response: str) -> dict:
    """Parse routing rules from LLM response."""
    rules = {
        "queue": [],
        "rules": {},
        "contexts": {},
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ROUTING_RULES:"):
            rules_str = line.split(":", 1)[-1].strip()
            if rules_str:
                rules["rules"]["routing"] = rules_str

        elif line.startswith("CHANNEL_PRIORITY:"):
            priority_str = line.split(":", 1)[-1].strip()
            if priority_str:
                priorities = [p.strip().strip("[](),") for p in priority_str.split(",")]
                rules["rules"]["priority"] = priorities

        elif line.startswith("CONTEXT_RETENTION:"):
            context_str = line.split(":", 1)[-1].strip()
            if context_str:
                rules["rules"]["context"] = context_str

        elif line.startswith("CONFIDENCE:"):
            try:
                rules["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                rules["confidence"] = 0.75

    return rules


def _integrate_external_tools(llm: LLMFn, state: FullAgentState) -> dict:
    """Integrate external tools and services."""
    prompt = f"""Integrate external tools for the AGI system:

Available Tools: Google Drive, Notion, Calendar
Current Phase 11 Status: {state.get('user_status', 'active')}
Assistant Ready: {state.get('assistant_ready', False)}

Provide:
EXTERNAL_TOOLS: [list of tools to integrate]
GOOGLE_DRIVE_ACCESS: [read/write capabilities]
NOTION_ACCESS: [read/write capabilities]
CALENDAR_ACCESS: [event management capabilities]
AVAILABLE_INTEGRATIONS: [list of active integrations]
CAPABILITIES: [what each tool can do]
READY: [true/false]"""

    response = llm(prompt)
    return _parse_tool_integrations(response)


def _parse_tool_integrations(response: str) -> dict:
    """Parse tool integration configuration."""
    tools = {
        "tools": [],
        "connections": {},
        "available": [],
        "ready": False,
        "capabilities": {},
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("EXTERNAL_TOOLS:"):
            tools_str = line.split(":", 1)[-1].strip()
            if tools_str:
                tool_list = [t.strip().strip("[](),") for t in tools_str.split(",")]
                tools["tools"] = [t for t in tool_list if t]

        elif line.startswith("GOOGLE_DRIVE_ACCESS:"):
            access = line.split(":", 1)[-1].strip()
            if access:
                tools["connections"]["google_drive"] = access
                tools["available"].append("Google Drive")
                tools["capabilities"]["Google Drive"] = ["read_files", "write_files", "share"]

        elif line.startswith("NOTION_ACCESS:"):
            access = line.split(":", 1)[-1].strip()
            if access:
                tools["connections"]["notion"] = access
                tools["available"].append("Notion")
                tools["capabilities"]["Notion"] = ["read_pages", "create_pages", "update_pages"]

        elif line.startswith("CALENDAR_ACCESS:"):
            access = line.split(":", 1)[-1].strip()
            if access:
                tools["connections"]["calendar"] = access
                tools["available"].append("Calendar")
                tools["capabilities"]["Calendar"] = ["create_event", "read_events", "update_event"]

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            tools["ready"] = ready_str in ["true", "yes", "1"]

    return tools
