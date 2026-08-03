"""Tests for Phase 19: Personality & Conversational Charm."""
import pytest
from agents.phase19_personality import (
    make_personality_framework_node,
    make_conversational_generation_node,
    make_personal_relationship_model_node,
    make_character_expression_summary_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Define an engaging AI personality" in prompt:
        return """TRAITS: [witty, charming, intelligent, loyal, wise]
VOICE: Sophisticated and warm with subtle humor
HUMOR_LEVEL: 0.7
FORMALITY_LEVEL: 0.65
CHARM_SCORE: 0.85
CONFIDENCE: 0.92"""
    elif "Generate a response with personality" in prompt:
        return """RESPONSE: I appreciate that question - it's exactly the kind of thinking I admire.
WIT_LEVEL: 0.75
CHARM_APPLIED: 0.8
CONFIDENCE: 0.88"""
    elif "Build personal relationship understanding" in prompt:
        return """QUIRKS: [prefers detailed explanations, values efficiency, appreciates wit]
PREFERENCES: [clear communication, direct feedback, occasional humor]
RELATIONSHIP_DEPTH: 0.72
PERSONALIZATION: 0.78
CONFIDENCE: 0.85"""
    return ""


def test_personality_framework_node():
    """Test Phase 19a personality framework node."""
    node = make_personality_framework_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Define personality",
        "core_mission": "Help users effectively",
    }

    result = node(state)

    assert len(result["personality_traits"]) > 0
    assert result["personality_traits"][0] in ["witty", "charming", "intelligent", "loyal", "wise"]
    assert len(result["character_voice"]) > 0
    assert result["humor_level"] > 0.5
    assert result["formality_level"] > 0.5
    assert result["charm_score"] > 0.5
    assert result["personality_confidence"] > 0.9


def test_personality_framework_node_no_mission():
    """Test personality framework with no mission."""
    node = make_personality_framework_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No mission",
    }

    result = node(state)

    assert isinstance(result["personality_traits"], list)
    assert isinstance(result["character_voice"], str)
    assert isinstance(result["humor_level"], float)
    assert isinstance(result["formality_level"], float)
    assert isinstance(result["charm_score"], float)
    assert isinstance(result["personality_confidence"], float)


def test_conversational_generation_node():
    """Test Phase 19b conversational generation node."""
    node = make_conversational_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "How can you help me today?",
        "personality_traits": ["witty", "charming", "intelligent"],
    }

    result = node(state)

    assert len(result["conversational_response"]) > 0
    assert result["response_wit_level"] >= 0.0
    assert result["response_charm_applied"] >= 0.0
    assert result["natural_dialogue_confidence"] > 0.0


def test_conversational_generation_node_no_traits():
    """Test conversational generation with no personality traits."""
    node = make_conversational_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Hello",
        "personality_traits": [],
    }

    result = node(state)

    assert result["conversational_response"] == ""
    assert result["response_wit_level"] == 0.0
    assert result["response_charm_applied"] == 0.0
    assert result["natural_dialogue_confidence"] == 0.0


def test_conversational_generation_node_no_input():
    """Test conversational generation with no input text."""
    node = make_conversational_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "",
        "personality_traits": ["witty", "charming"],
    }

    result = node(state)

    assert result["conversational_response"] == ""
    assert result["response_wit_level"] == 0.0
    assert result["response_charm_applied"] == 0.0
    assert result["natural_dialogue_confidence"] == 0.0


def test_personal_relationship_model_node():
    """Test Phase 19c personal relationship model node."""
    node = make_personal_relationship_model_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Build relationship",
        "user_profile": {"name": "Alice"},
        "user_patterns": ["asks detailed questions", "values efficiency"],
        "execution_history": [
            {"task": "task1", "outcome": "success"},
            {"task": "task2", "outcome": "partial"},
        ],
    }

    result = node(state)

    assert isinstance(result["user_quirks"], list)
    assert isinstance(result["user_preferences_learned"], dict)
    assert result["relationship_depth"] > 0.0
    assert result["personalization_level"] > 0.0
    assert result["relationship_confidence"] > 0.0


def test_personal_relationship_model_node_empty():
    """Test personal relationship model with no profile or patterns."""
    node = make_personal_relationship_model_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty",
        "user_profile": {},
        "user_patterns": [],
    }

    result = node(state)

    assert result["user_quirks"] == []
    assert result["user_preferences_learned"] == {}
    assert result["relationship_depth"] == 0.0
    assert result["personalization_level"] == 0.0
    assert result["relationship_confidence"] == 0.0


def test_character_expression_summary_node():
    """Test Phase 19d character expression summary node."""
    node = make_character_expression_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate summary",
        "personality_traits": ["witty", "charming", "intelligent"],
        "charm_score": 0.85,
        "humor_level": 0.7,
        "formality_level": 0.65,
        "relationship_depth": 0.72,
        "personalization_level": 0.78,
        "user_quirks": ["prefers detailed explanations", "values efficiency"],
        "conversational_response": "I appreciate that question - it's exactly the kind of thinking I admire.",
        "personality_confidence": 0.92,
        "natural_dialogue_confidence": 0.88,
    }

    result = node(state)

    assert result["personality_established"] is True
    assert result["character_ready"] is True
    assert result["conversational_charm_active"] is True
    assert "Personality & Conversational Charm" in result["phase19_summary"]
    assert "Personality Profile" in result["phase19_summary"]
    assert "Charm & Wit Assessment" in result["phase19_summary"]


def test_character_expression_summary_node_minimal():
    """Test character expression summary with minimal data."""
    node = make_character_expression_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Minimal",
    }

    result = node(state)

    assert result["personality_established"] is True
    assert result["character_ready"] is True
    assert result["conversational_charm_active"] is True
    assert "Personality & Conversational Charm" in result["phase19_summary"]


def test_personality_traits_parsing():
    """Test personality traits parsing from response."""
    node = make_personality_framework_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
    }

    result = node(state)

    assert isinstance(result["personality_traits"], list)
    for trait in result["personality_traits"]:
        assert isinstance(trait, str)
        assert len(trait) > 0


def test_conversation_response_parsing():
    """Test conversation response parsing."""
    node = make_conversational_generation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test response",
        "personality_traits": ["witty", "intelligent"],
    }

    result = node(state)

    assert isinstance(result["conversational_response"], str)
    assert isinstance(result["response_wit_level"], float)
    assert isinstance(result["response_charm_applied"], float)
    assert isinstance(result["natural_dialogue_confidence"], float)


def test_relationship_depth_tracking():
    """Test relationship depth tracking over multiple interactions."""
    node = make_personal_relationship_model_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Track relationship",
        "user_profile": {"name": "Bob", "interaction_count": 10},
        "user_patterns": ["pattern1", "pattern2", "pattern3"],
        "execution_history": list(range(10)),  # Simulate 10 interactions
    }

    result = node(state)

    assert result["relationship_depth"] >= 0.0
    assert result["relationship_depth"] <= 1.0
    assert result["personalization_level"] >= 0.0
    assert result["personalization_level"] <= 1.0
    assert result["relationship_confidence"] >= 0.0
    assert result["relationship_confidence"] <= 1.0


def test_full_personality_pipeline():
    """Test full personality pipeline from framework to summary."""
    framework_node = make_personality_framework_node(fake_llm)
    conversation_node = make_conversational_generation_node(fake_llm)
    relationship_node = make_personal_relationship_model_node(fake_llm)
    summary_node = make_character_expression_summary_node(fake_llm)

    state: FullAgentState = {
        "input_text": "Hello, can you help me?",
        "core_mission": "Assist users effectively",
        "user_profile": {"name": "User"},
        "user_patterns": ["direct communication"],
        "execution_history": [],
    }

    # Step 1: Establish personality
    state = framework_node(state)
    assert len(state["personality_traits"]) > 0
    assert "personality_established" not in state  # Not set until summary node

    # Step 2: Generate conversation
    state = conversation_node(state)
    assert len(state["conversational_response"]) > 0

    # Step 3: Build relationship
    state = relationship_node(state)
    assert state["relationship_depth"] >= 0.0

    # Step 4: Generate summary
    state = summary_node(state)
    assert state["personality_established"] is True
    assert state["character_ready"] is True
    assert state["conversational_charm_active"] is True
    assert "phase19_summary" in state
    assert len(state["phase19_summary"]) > 0
