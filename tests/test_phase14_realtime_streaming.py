"""Tests for Phase 14: Real-Time Event Streaming & Continuous Monitoring."""
import pytest
from agents.phase14_realtime_streaming import (
    make_event_listener_node,
    make_event_processor_node,
    make_response_generator_node,
    make_streaming_summary_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Setup real-time event streaming" in prompt:
        return """EVENT_STREAMS: [Slack API, Discord Webhooks, Email IMAP]
MONITORED_SOURCES: [#channel-updates, bot-notifications, user-inbox]
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
RESPONSE_LATENCY_MS: 85
RESPONSE_QUEUE: [send_email, update_dashboard]
READY: true
CONFIDENCE: 0.80"""
    return ""


def test_event_listener_node():
    """Test Phase 14a event listener node."""
    node = make_event_listener_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Monitor all events",
        "active_channels": ["slack", "discord"],
        "installed_plugins": ["webhook_manager", "event_aggregator"],
        "multichannel_ready": True,
    }

    result = node(state)

    assert result["listener_ready"] is True
    assert len(result["event_streams"]) > 0
    assert "Slack API" in result["event_streams"][0]
    assert result["streaming_confidence"] > 0.8


def test_event_processor_node():
    """Test Phase 14b event processor node."""
    node = make_event_processor_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Process events",
        "event_streams": ["Slack API", "Discord Webhooks"],
        "event_queue": [],
    }

    result = node(state)

    assert result["event_processing_confidence"] > 0.0
    assert len(result["processed_events"]) > 0
    assert len(result["triggered_actions"]) > 0


def test_event_processor_node_empty_streams():
    """Test event processor with no streams."""
    node = make_event_processor_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No events",
        "event_streams": [],
    }

    result = node(state)

    assert result["processed_events"] == []
    assert result["event_queue"] == []
    assert result["triggered_actions"] == []


def test_response_generator_node():
    """Test Phase 14c response generator node."""
    node = make_response_generator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate responses",
        "processed_events": ["message_received", "user_joined"],
    }

    result = node(state)

    assert result["response_confidence"] > 0.0
    assert len(result["realtime_responses"]) > 0
    assert result["response_latency_ms"] >= 0


def test_response_generator_node_empty_events():
    """Test response generator with no events."""
    node = make_response_generator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No events",
        "processed_events": [],
    }

    result = node(state)

    assert result["realtime_responses"] == []
    assert result["response_queue"] == []
    assert result["response_latency_ms"] == 0


def test_streaming_summary_node():
    """Test Phase 14d streaming summary node."""
    node = make_streaming_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate summary",
        "event_streams": ["Slack API", "Discord Webhooks"],
        "monitored_sources": ["#channel-updates", "bot-notifications"],
        "processed_events": ["message_received", "user_joined"],
        "realtime_responses": ["Send acknowledgment", "Escalate to team"],
        "streaming_confidence": 0.85,
        "response_latency_ms": 85,
    }

    result = node(state)

    assert result["realtime_streaming_ready"] is True
    assert "Real-Time Streaming Mode" in result["phase14_summary"]
    assert "Active Event Streams" in result["phase14_summary"]


def test_streaming_summary_node_empty():
    """Test streaming summary with minimal data."""
    node = make_streaming_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty summary",
    }

    result = node(state)

    assert result["realtime_streaming_ready"] is True
    assert "Real-Time Streaming Mode" in result["phase14_summary"]


def test_event_listener_response_parsing():
    """Test event listener response parsing with various formats."""
    node = make_event_listener_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
        "active_channels": [],
        "installed_plugins": [],
    }

    result = node(state)

    assert isinstance(result["event_streams"], list)
    assert isinstance(result["monitored_sources"], list)
    assert isinstance(result["streaming_confidence"], float)
    assert 0.0 <= result["streaming_confidence"] <= 1.0


def test_event_processor_action_parsing():
    """Test event processor action parsing."""
    node = make_event_processor_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test action parsing",
        "event_streams": ["test_stream"],
    }

    result = node(state)

    assert isinstance(result["triggered_actions"], list)
    assert isinstance(result["event_queue"], list)
    assert len(result["triggered_actions"]) > 0
