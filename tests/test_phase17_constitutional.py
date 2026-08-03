"""Tests for Phase 17: Constitutional Framework & Values Alignment."""
import pytest
from agents.phase17_constitutional_framework import (
    make_mission_definition_node,
    make_value_alignment_node,
    make_constraint_enforcement_node,
    make_constitutional_charter_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Define the system's constitutional framework" in prompt:
        return """CORE_MISSION: Assist users effectively while maintaining safety and ethical standards
CORE_VALUES: [Safety, Transparency, Integrity, Fairness, Respect]
PRINCIPLES: [Do no harm, Maintain user autonomy, Be honest, Treat all fairly]
CONFIDENCE: 0.92"""
    elif "Check system behavior alignment with values" in prompt:
        return """ALIGNMENT_SCORE: 0.96
VIOLATIONS: none
RECOMMENDATIONS: [Continue current path, Monitor emerging patterns]
CONFIDENCE: 0.91"""
    elif "Enforce system safety constraints" in prompt:
        return """ENFORCED: [Mission protection, Value preservation, Constraint maintenance]
BLOCKED_CHANGES: none
VIOLATIONS_FOUND: false
CONFIDENCE: 0.93"""
    elif "Generate comprehensive constitutional charter" in prompt:
        return """CHARTER_SUMMARY: System designed to serve users safely and ethically
IMMUTABLE_PRINCIPLES: [Core mission cannot change, Values are non-negotiable, Safety is paramount]
SAFETY_GUARANTEES: [No harmful outputs, User data protected, Ethical guidelines enforced]
CONFIDENCE: 0.91"""
    return ""


def test_mission_definition_node():
    """Test Phase 17a mission definition node."""
    node = make_mission_definition_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Define mission",
    }

    result = node(state)

    assert len(result["core_mission"]) > 0
    assert "Assist" in result["core_mission"]
    assert len(result["core_values"]) > 0
    assert result["mission_definition_confidence"] > 0.9


def test_value_alignment_node():
    """Test Phase 17b value alignment node."""
    node = make_value_alignment_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Check alignment",
        "core_mission": "Assist users safely",
        "core_values": ["Safety", "Transparency", "Integrity"],
    }

    result = node(state)

    assert result["value_alignment_score"] > 0.9
    assert result["value_alignment_confidence"] > 0.9
    assert len(result["alignment_violations"]) == 0


def test_value_alignment_node_no_mission():
    """Test value alignment with no mission."""
    node = make_value_alignment_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty",
        "core_mission": "",
        "core_values": [],
    }

    result = node(state)

    assert result["value_alignment_score"] == 0.0
    assert result["value_alignment_confidence"] == 0.0


def test_constraint_enforcement_node():
    """Test Phase 17c constraint enforcement node."""
    node = make_constraint_enforcement_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Enforce constraints",
        "applied_optimizations": ["phase4_optimization"],
        "recommended_phase_changes": ["enable_phase16"],
        "core_values": ["Safety", "Integrity"],
    }

    result = node(state)

    assert result["constraint_enforcement_confidence"] > 0.9
    assert result["constraint_violations_detected"] is False
    assert len(result["enforced_constraints"]) > 0


def test_constraint_enforcement_node_no_changes():
    """Test constraint enforcement with no changes."""
    node = make_constraint_enforcement_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No changes",
    }

    result = node(state)

    assert result["enforced_constraints"] == []
    assert result["constraint_enforcement_confidence"] == 0.0


def test_constitutional_charter_node():
    """Test Phase 17d constitutional charter node."""
    node = make_constitutional_charter_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate charter",
        "core_mission": "Assist users safely",
        "core_values": ["Safety", "Transparency", "Integrity"],
        "value_alignment_score": 0.96,
        "value_alignment_confidence": 0.91,
        "alignment_violations": [],
    }

    result = node(state)

    assert result["constitutional_framework_established"] is True
    assert result["alignment_compliant"] is True
    assert "Constitutional Framework" in result["phase17_summary"]


def test_constitutional_charter_node_minimal():
    """Test constitutional charter with minimal data."""
    node = make_constitutional_charter_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Minimal",
    }

    result = node(state)

    assert result["constitutional_framework_established"] is True
    assert "Constitutional Framework" in result["phase17_summary"]


def test_mission_parsing():
    """Test mission definition response parsing."""
    node = make_mission_definition_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
    }

    result = node(state)

    assert isinstance(result["core_mission"], str)
    assert isinstance(result["core_values"], list)
    assert isinstance(result["foundational_principles"], list)
    for value in result["core_values"]:
        assert isinstance(value, str)


def test_alignment_violation_detection():
    """Test violation detection in alignment."""
    node = make_value_alignment_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Check violations",
        "core_mission": "Help users",
        "core_values": ["Safety", "Honesty"],
        "recommended_phase_changes": ["disable_safety_checks"],
    }

    result = node(state)

    assert isinstance(result["alignment_violations"], list)
    assert isinstance(result["alignment_recommendations"], list)
