"""Tests for Phase 21: Voice & Natural Conversation Interface."""
import pytest
from agents.phase21_voice_conversation import (
    make_voice_processing_node,
    make_conversation_flow_node,
    make_tts_generation_node,
    make_voice_interface_summary_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Process voice input and transcribe" in prompt:
        return """SPEECH_DETECTED: true
TRANSCRIBED_TEXT: Hello, how can I assist you today?
SPEECH_CONFIDENCE: 0.92
SPEECH_TONE: calm
VOICE_CHARACTERISTICS: Female voice, professional tone, slight accent"""
    elif "Manage natural conversation flow" in prompt:
        return """CONVERSATION_FLOW: [User asks question, Assistant responds, User clarifies]
NATURAL_PAUSES: [500ms, 300ms, 400ms]
INTERRUPTION_POINTS: [After greeting, After explanation]
CONTEXT: {'topic': 'assistance', 'intent': 'seeking_help'}
CONFIDENCE: 0.85"""
    elif "Generate natural speech from text" in prompt:
        return """SPEECH_RATE: 160
PROSODY_MARKERS: [Emphasis at "assist", Slight pause after "today"]
EMPHASIS_POINTS: [assist, question, help]
READY: true
CONFIDENCE: 0.88"""
    return ""


def test_voice_processing_node():
    """Test Phase 21a voice processing node."""
    node = make_voice_processing_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Voice input detected",
        "user_profile": {"name": "user"},
    }

    result = node(state)

    assert result["speech_detected"] is True
    assert len(result["transcribed_text"]) > 0
    assert result["speech_confidence"] > 0.8
    assert result["speech_tone"] != ""


def test_voice_processing_node_no_input():
    """Test voice processing with no input."""
    node = make_voice_processing_node(fake_llm)
    state: FullAgentState = {
        "input_text": "",
    }

    result = node(state)

    assert isinstance(result["speech_detected"], bool)
    assert isinstance(result["transcribed_text"], str)
    assert isinstance(result["speech_confidence"], float)


def test_conversation_flow_node():
    """Test Phase 21b conversation flow node."""
    node = make_conversation_flow_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test conversation",
        "transcribed_text": "Hello, how can I assist you today?",
        "emotional_state": "neutral",
    }

    result = node(state)

    assert isinstance(result["conversation_flow"], list)
    assert isinstance(result["natural_pauses"], list)
    assert isinstance(result["interruption_points"], list)
    assert result["conversation_confidence"] > 0.0


def test_conversation_flow_node_empty():
    """Test conversation flow with no transcription."""
    node = make_conversation_flow_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No speech",
        "transcribed_text": "",
    }

    result = node(state)

    assert result["conversation_context"] == {}
    assert result["conversation_flow"] == []
    assert result["natural_pauses"] == []
    assert result["interruption_points"] == []


def test_tts_generation_node():
    """Test Phase 21c TTS generation node."""
    node = make_tts_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate speech",
        "empathetic_response": "I appreciate your question. Let me help you.",
        "response_tone_adjustment": "warm",
        "emotional_support_level": 0.7,
        "user_profile": {"name": "JARVIS"},
    }

    result = node(state)

    assert len(result["spoken_response"]) > 0
    assert result["speech_rate"] > 0
    assert isinstance(result["prosody_markers"], list)
    assert isinstance(result["emphasis_points"], list)


def test_tts_generation_node_empty():
    """Test TTS generation with no response."""
    node = make_tts_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No response",
        "empathetic_response": "",
    }

    result = node(state)

    assert result["spoken_response"] == ""
    assert result["tts_ready"] is False
    assert result["speech_rate"] == 150


def test_voice_interface_summary_node():
    """Test Phase 21d voice interface summary node."""
    node = make_voice_interface_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate voice summary",
        "speech_detected": True,
        "transcribed_text": "Hello, how can I assist you?",
        "speech_confidence": 0.92,
        "speech_tone": "calm",
        "conversation_flow": ["User asks", "Assistant responds"],
        "natural_pauses": ["500ms", "300ms"],
        "spoken_response": "I appreciate your question.",
        "speech_rate": 160,
        "prosody_markers": ["emphasis"],
        "emphasis_points": ["assist"],
        "tts_ready": True,
        "tts_confidence": 0.88,
        "conversation_confidence": 0.85,
    }

    result = node(state)

    assert result["voice_interface_ready"] is True
    assert "Voice & Conversation Interface" in result["phase21_summary"]
    assert "Voice Input Detected" in result["phase21_summary"]


def test_voice_interface_summary_node_minimal():
    """Test voice interface summary with minimal data."""
    node = make_voice_interface_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Minimal summary",
    }

    result = node(state)

    assert result["voice_interface_ready"] is True
    assert "Voice & Conversation Interface" in result["phase21_summary"]


def test_speech_confidence_parsing():
    """Test speech confidence parsing."""
    node = make_voice_processing_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test confidence",
    }

    result = node(state)

    assert isinstance(result["speech_confidence"], float)
    assert 0.0 <= result["speech_confidence"] <= 1.0


def test_speech_rate_parsing():
    """Test speech rate parsing."""
    node = make_tts_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test rate",
        "empathetic_response": "Test response",
    }

    result = node(state)

    assert isinstance(result["speech_rate"], int)
    assert 100 <= result["speech_rate"] <= 200  # Reasonable speech rate range
