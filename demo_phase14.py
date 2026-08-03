"""Demo: Phase 14 - Real-Time Event Streaming & Continuous Monitoring."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Demonstrate real-time event streaming\nENTITIES: events, monitoring, real-time"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: Event streaming best practices\nSUMMARY: Streaming enables low-latency event processing"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: event_quality, latency, throughput\nMETACOGNITIVE_NOTES: Focus on performance"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Causal\nREASONING_STEPS: [Identify sources, Process events, Generate responses]\nREASONING_CONCLUSION: Streaming enables real-time responses"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Event batching, Predictive routing]\nANALOGIES: [River flow, Traffic management]\nNOVEL_COMBINATIONS: [ML-based event prioritization]"
    elif "Setup real-time event streaming" in prompt:
        return """EVENT_STREAMS: [Slack API, Discord Webhooks, Email IMAP]
MONITORED_SOURCES: [#announcements, #alerts, inbox]
LISTENER_STATUS: active
READY: true
CONFIDENCE: 0.85"""
    elif "Process real-time events" in prompt:
        return """PROCESSED_EVENTS: [message_received, user_joined, alert_triggered]
EVENT_QUEUE: [priority_alert, scheduled_reminder]
TRIGGERED_ACTIONS: [notify_user, log_event, update_cache]
READY: true
CONFIDENCE: 0.82"""
    elif "Generate real-time responses" in prompt:
        return """REALTIME_RESPONSES: [Send acknowledgment, Escalate to team, Log for audit]
RESPONSE_LATENCY_MS: 78
RESPONSE_QUEUE: [send_email, update_dashboard]
READY: true
CONFIDENCE: 0.80"""
    return ""


def main():
    """Run Phase 14 demo."""
    print("\n" + "=" * 80)
    print("PHASE 14: Real-Time Event Streaming & Continuous Monitoring")
    print("=" * 80)

    # Initialize coordinator with Phase 14 enabled
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=True,
        enable_phase15=False,
        enable_phase21=False,
    )

    # Create input state
    state: FullAgentState = {
        "input_text": "Monitor events from Slack, Discord, and email and generate real-time responses",
        "active_channels": ["slack", "discord", "email"],
        "installed_plugins": ["webhook_manager", "event_aggregator", "response_engine"],
        "multichannel_ready": True,
    }

    print("\n📥 Input:")
    print(f"  Message: {state['input_text']}")
    print(f"  Active Channels: {state['active_channels']}")
    print(f"  Plugins: {state['installed_plugins']}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Display results
    print("\n🌊 Phase 14a: Event Listener")
    print(f"  Listener Ready: {result.get('listener_ready', False)}")
    print(f"  Event Streams: {result.get('event_streams', [])}")
    print(f"  Monitored Sources: {result.get('monitored_sources', [])}")
    print(f"  Status: {result.get('listener_status', 'unknown')}")
    print(f"  Confidence: {result.get('streaming_confidence', 0):.0%}")

    print("\n⚡ Phase 14b: Event Processor")
    print(f"  Processed Events: {result.get('processed_events', [])}")
    print(f"  Event Queue: {result.get('event_queue', [])}")
    print(f"  Triggered Actions: {result.get('triggered_actions', [])}")
    print(f"  Confidence: {result.get('event_processing_confidence', 0):.0%}")

    print("\n💬 Phase 14c: Response Generator")
    print(f"  Real-Time Responses: {result.get('realtime_responses', [])}")
    print(f"  Response Latency: {result.get('response_latency_ms', 0)}ms")
    print(f"  Response Queue: {result.get('response_queue', [])}")
    print(f"  Confidence: {result.get('response_confidence', 0):.0%}")

    print("\n📊 Phase 14d: Streaming Summary")
    print(result.get("phase14_summary", "No summary"))

    print("\n✨ System Status:")
    print(f"  Streaming Ready: {result.get('realtime_streaming_ready', False)}")
    print(f"  Total Latency: {result.get('response_latency_ms', 0)}ms")

    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
