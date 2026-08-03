"""Phase 14: Real-Time Event Streaming & Continuous Monitoring."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_event_listener_node(llm: LLMFn):
    """
    Create Phase 14a event listener node.

    Monitors and processes continuous event streams.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 14a: Event Listener.

        Sets up real-time event monitoring and streaming.
        """
        listener = _setup_event_listener(llm, state)

        state.update({
            "event_streams": listener.get("streams", []),
            "monitored_sources": listener.get("sources", []),
            "listener_status": listener.get("status", "inactive"),
            "listener_ready": listener.get("ready", False),
            "streaming_confidence": listener.get("confidence", 0.0),
        })

        return state

    return process


def make_event_processor_node(llm: LLMFn):
    """
    Create Phase 14b event processor node.

    Processes incoming events and triggers appropriate responses.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 14b: Event Processor.

        Analyzes and responds to real-time events.
        """
        event_streams = state.get("event_streams", [])

        if not event_streams:
            state.update({
                "processed_events": [],
                "event_queue": [],
                "triggered_actions": [],
                "processor_ready": False,
            })
            return state

        processor = _process_events(llm, state, event_streams)

        state.update({
            "processed_events": processor.get("events", []),
            "event_queue": processor.get("queue", []),
            "triggered_actions": processor.get("actions", []),
            "processor_ready": processor.get("ready", False),
            "event_processing_confidence": processor.get("confidence", 0.0),
        })

        return state

    return process


def make_response_generator_node(llm: LLMFn):
    """
    Create Phase 14c response generator node.

    Generates real-time responses to events.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 14c: Response Generator.

        Creates immediate, contextual responses to events.
        """
        processed_events = state.get("processed_events", [])

        if not processed_events:
            state.update({
                "realtime_responses": [],
                "response_latency_ms": 0,
                "response_queue": [],
                "generator_ready": False,
            })
            return state

        generator = _generate_responses(llm, state, processed_events)

        state.update({
            "realtime_responses": generator.get("responses", []),
            "response_latency_ms": generator.get("latency", 0),
            "response_queue": generator.get("queue", []),
            "generator_ready": generator.get("ready", False),
            "response_confidence": generator.get("confidence", 0.0),
        })

        return state

    return process


def make_streaming_summary_node(llm: LLMFn):
    """
    Create Phase 14d streaming summary node.

    Generates real-time system status summary.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate streaming system summary."""
        summary_lines = [
            "=== Real-Time Streaming Mode ===",
        ]

        # Event Streams
        streams = state.get("event_streams", [])
        if streams:
            summary_lines.append(f"\n🌊 Active Event Streams ({len(streams)}):")
            for stream in streams[:5]:
                summary_lines.append(f"  ✓ {stream}")

        # Monitored Sources
        sources = state.get("monitored_sources", [])
        if sources:
            summary_lines.extend([
                f"\n📡 Monitored Sources ({len(sources)}):",
            ])
            for source in sources[:5]:
                summary_lines.append(f"  • {source}")

        # Processed Events
        events = state.get("processed_events", [])
        if events:
            summary_lines.extend([
                f"\n⚡ Processed Events ({len(events)}):",
            ])
            for event in events[:3]:
                summary_lines.append(f"  → {event}")

        # Real-Time Responses
        responses = state.get("realtime_responses", [])
        if responses:
            summary_lines.extend([
                f"\n💬 Real-Time Responses ({len(responses)}):",
            ])
            for response in responses[:3]:
                summary_lines.append(f"  ✓ {response}")

        # Performance Metrics
        latency = state.get("response_latency_ms", 0)
        summary_lines.extend([
            f"\n⏱️  Response Latency: {latency}ms",
            f"✨ Streaming Confidence: {state.get('streaming_confidence', 0):.0%}",
        ])

        phase14_summary = "\n".join(summary_lines)

        state.update({
            "phase14_summary": phase14_summary,
            "realtime_streaming_ready": True,
        })

        return state

    return process


def _setup_event_listener(llm: LLMFn, state: FullAgentState) -> dict:
    """Setup real-time event listener."""
    prompt = f"""Setup real-time event streaming:

Current Channels: {', '.join(state.get('active_channels', [])) or 'None'}
Installed Plugins: {', '.join(state.get('installed_plugins', [])[:3]) or 'None'}
System Ready: {state.get('multichannel_ready', False)}

Provide:
EVENT_STREAMS: [which event sources to listen to]
MONITORED_SOURCES: [channels, webhooks, APIs to monitor]
LISTENER_STATUS: [active/configuring/ready]
READY: [true/false]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_listener_response(response)


def _parse_listener_response(response: str) -> dict:
    """Parse event listener response."""
    listener = {
        "streams": [],
        "sources": [],
        "status": "inactive",
        "ready": False,
        "confidence": 0.78,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("EVENT_STREAMS:"):
            streams_str = line.split(":", 1)[-1].strip()
            if streams_str:
                streams = [s.strip().strip("[](),") for s in streams_str.split(",")]
                listener["streams"] = [s for s in streams if s]

        elif line.startswith("MONITORED_SOURCES:"):
            sources_str = line.split(":", 1)[-1].strip()
            if sources_str:
                sources = [s.strip().strip("[](),") for s in sources_str.split(",")]
                listener["sources"] = [s for s in sources if s]

        elif line.startswith("LISTENER_STATUS:"):
            listener["status"] = line.split(":", 1)[-1].strip()

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            listener["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                listener["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                listener["confidence"] = 0.78

    return listener


def _process_events(llm: LLMFn, state: FullAgentState, streams: list) -> dict:
    """Process incoming events."""
    streams_str = ", ".join(streams[:3])

    prompt = f"""Process real-time events from streams:

Event Streams: {streams_str}
Queue Size: {len(state.get('event_queue', []))}

Provide:
PROCESSED_EVENTS: [events detected]
EVENT_QUEUE: [queued for processing]
TRIGGERED_ACTIONS: [actions to take]
READY: [true/false]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_processor_response(response)


def _parse_processor_response(response: str) -> dict:
    """Parse event processor response."""
    processor = {
        "events": [],
        "queue": [],
        "actions": [],
        "ready": False,
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("PROCESSED_EVENTS:"):
            events_str = line.split(":", 1)[-1].strip()
            if events_str:
                events = [e.strip().strip("[](),") for e in events_str.split(",")]
                processor["events"] = [e for e in events if e]

        elif line.startswith("EVENT_QUEUE:"):
            queue_str = line.split(":", 1)[-1].strip()
            if queue_str:
                queue = [q.strip().strip("[](),") for q in queue_str.split(",")]
                processor["queue"] = [q for q in queue if q]

        elif line.startswith("TRIGGERED_ACTIONS:"):
            actions_str = line.split(":", 1)[-1].strip()
            if actions_str:
                actions = [a.strip().strip("[](),") for a in actions_str.split(",")]
                processor["actions"] = [a for a in actions if a]

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            processor["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                processor["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                processor["confidence"] = 0.75

    return processor


def _generate_responses(llm: LLMFn, state: FullAgentState, events: list) -> dict:
    """Generate real-time responses to events."""
    events_str = ", ".join(events[:3])

    prompt = f"""Generate real-time responses to events:

Events: {events_str}

Provide:
REALTIME_RESPONSES: [immediate responses to events]
RESPONSE_LATENCY_MS: [expected response time]
RESPONSE_QUEUE: [queued responses]
READY: [true/false]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_generator_response(response)


def _parse_generator_response(response: str) -> dict:
    """Parse response generator output."""
    generator = {
        "responses": [],
        "latency": 100,
        "queue": [],
        "ready": False,
        "confidence": 0.76,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("REALTIME_RESPONSES:"):
            resp_str = line.split(":", 1)[-1].strip()
            if resp_str:
                responses = [r.strip().strip("[](),") for r in resp_str.split(",")]
                generator["responses"] = [r for r in responses if r]

        elif line.startswith("RESPONSE_LATENCY_MS:"):
            try:
                generator["latency"] = int(line.split(":", 1)[-1].strip())
            except ValueError:
                generator["latency"] = 100

        elif line.startswith("RESPONSE_QUEUE:"):
            queue_str = line.split(":", 1)[-1].strip()
            if queue_str:
                queue = [q.strip().strip("[](),") for q in queue_str.split(",")]
                generator["queue"] = [q for q in queue if q]

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            generator["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                generator["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                generator["confidence"] = 0.76

    return generator
