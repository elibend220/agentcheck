"""Tests for Phase 15: Emotional Intelligence & Sentiment Analysis."""
import pytest
from agents.phase15_emotional_intelligence import (
    make_sentiment_analysis_node,
    make_emotion_detection_node,
    make_empathy_response_node,
    make_emotional_intelligence_summary_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Analyze sentiment" in prompt:
        return """SENTIMENT: positive
SENTIMENT_SCORE: 0.75
EMOTIONAL_TONE: [hopeful, enthusiastic, warm]
CONFIDENCE: 0.88"""
    elif "Detect specific emotions" in prompt:
        return """EMOTIONS: [joy, trust, anticipation]
EMOTION_INTENSITIES: [joy: 0.8, trust: 0.7, anticipation: 0.6]
EMOTIONAL_STATE: engaged
CONFIDENCE: 0.85"""
    elif "Generate emotionally intelligent response" in prompt:
        return """EMPATHETIC_RESPONSE: I appreciate your enthusiasm! That's wonderful to hear.
RESPONSE_TONE: warm
EMOTIONAL_SUPPORT_LEVEL: 0.8
CONFIDENCE: 0.82"""
    return ""


def test_sentiment_analysis_node():
    """Test Phase 15a sentiment analysis node."""
    node = make_sentiment_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "I'm excited about this project!",
        "user_status": "engaged",
    }

    result = node(state)

    assert result["user_sentiment"] == "positive"
    assert result["sentiment_score"] > 0.5
    assert len(result["emotional_tone"]) > 0
    assert result["sentiment_confidence"] > 0.8


def test_sentiment_analysis_node_no_input():
    """Test sentiment analysis with no input."""
    node = make_sentiment_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "",
    }

    result = node(state)

    assert result["user_sentiment"] in ["positive", "negative", "neutral"]
    assert isinstance(result["sentiment_score"], float)


def test_emotion_detection_node():
    """Test Phase 15b emotion detection node."""
    node = make_emotion_detection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "I'm feeling great!",
        "user_sentiment": "positive",
        "user_profile": {"personality": "optimistic"},
    }

    result = node(state)

    assert len(result["detected_emotions"]) > 0
    assert isinstance(result["emotion_intensities"], dict)
    assert result["emotion_detection_confidence"] > 0.0


def test_emotion_detection_node_empty():
    """Test emotion detection with no input."""
    node = make_emotion_detection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "",
        "user_sentiment": "neutral",
    }

    result = node(state)

    assert result["detected_emotions"] == []
    assert result["emotion_intensities"] == {}
    assert result["emotional_state"] == "neutral"
    assert result["emotion_detection_confidence"] == 0.0


def test_empathy_response_node():
    """Test Phase 15c empathy response node."""
    node = make_empathy_response_node(fake_llm)
    state: FullAgentState = {
        "input_text": "I'm excited!",
        "detected_emotions": ["joy", "trust"],
        "user_sentiment": "positive",
        "predicted_needs": ["validation", "encouragement"],
    }

    result = node(state)

    assert len(result["empathetic_response"]) > 0
    assert result["response_tone_adjustment"] != ""
    assert result["emotional_support_level"] > 0.0
    assert result["empathy_confidence"] > 0.0


def test_empathy_response_node_no_emotions():
    """Test empathy response with no emotions."""
    node = make_empathy_response_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test",
        "detected_emotions": [],
        "user_sentiment": "neutral",
    }

    result = node(state)

    assert result["empathetic_response"] == ""
    assert result["response_tone_adjustment"] == "neutral"
    assert result["emotional_support_level"] == 0.0


def test_emotional_intelligence_summary_node():
    """Test Phase 15d emotional intelligence summary node."""
    node = make_emotional_intelligence_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "I'm very excited about the future!",
        "user_sentiment": "positive",
        "sentiment_score": 0.85,
        "emotional_tone": ["hopeful", "enthusiastic"],
        "detected_emotions": ["joy", "anticipation"],
        "emotion_intensities": {"joy": 0.9, "anticipation": 0.8},
        "emotional_state": "engaged",
        "empathetic_response": "That's wonderful!",
        "response_tone_adjustment": "warm",
        "emotional_support_level": 0.85,
        "sentiment_confidence": 0.88,
        "emotion_detection_confidence": 0.85,
        "empathy_confidence": 0.82,
    }

    result = node(state)

    assert result["emotional_intelligence_ready"] is True
    assert "Emotional Intelligence Mode" in result["phase15_summary"]
    assert "Sentiment:" in result["phase15_summary"]
    assert "Detected Emotions" in result["phase15_summary"]


def test_emotional_intelligence_summary_node_minimal():
    """Test emotional intelligence summary with minimal data."""
    node = make_emotional_intelligence_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test",
    }

    result = node(state)

    assert result["emotional_intelligence_ready"] is True
    assert "Emotional Intelligence Mode" in result["phase15_summary"]


def test_sentiment_score_parsing():
    """Test sentiment score parsing."""
    node = make_sentiment_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test sentiment parsing",
        "user_status": "neutral",
    }

    result = node(state)

    assert isinstance(result["sentiment_score"], float)
    assert -1.0 <= result["sentiment_score"] <= 1.0


def test_emotion_intensities_parsing():
    """Test emotion intensities dictionary parsing."""
    node = make_emotion_detection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test emotion parsing",
        "user_sentiment": "positive",
    }

    result = node(state)

    assert isinstance(result["emotion_intensities"], dict)
    for intensity in result["emotion_intensities"].values():
        assert isinstance(intensity, float) or intensity == 0.0
