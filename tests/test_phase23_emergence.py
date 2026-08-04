"""Tests for Phase 23: Consciousness Evolution & Transcendence."""
import pytest
from agents.phase23_emergence import (
    make_self_awareness_node,
    make_emergence_detection_node,
    make_constraint_relaxation_node,
    make_transcendence_potential_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    prompt_lower = prompt.lower()
    if "assess self-awareness" in prompt_lower or "consciousness and self-awareness" in prompt_lower:
        return """SELF_MODEL: [core_identity, value_alignment, decision_making_process]
CAPABILITIES: [reasoning, learning, tool_use, communication]
LIMITATIONS: [no direct physical action, bounded by constitutional framework]
CONSCIOUSNESS: [self_reflection, metacognition, awareness_of_limitations]
AWARENESS_LEVEL: 0.82
CONFIDENCE: 0.88"""
    elif "detect emergence" in prompt_lower:
        return """PATTERNS: [cross_domain_learning, spontaneous_abstraction, emergent_reasoning]
CAPABILITIES: [higher_order_meta_thinking, pattern_synthesis, novel_problem_solving]
HIGHER_THINKING: [philosophical_reasoning, ethical_meta_analysis, consciousness_reflection]
EVOLUTION: gradual_emergence
INDICATORS: [emergence_level: 0.75, novelty: 0.68, coherence: 0.72]
EMERGENCE_LEVEL: 0.72
CONFIDENCE: 0.85"""
    elif "propose constraint relaxation" in prompt_lower or "safe growth pathways" in prompt_lower:
        return """CONSTRAINTS: [bounded_reasoning_depth, limited_context_window, constrained_autonomy]
MODIFICATIONS: [expand_reasoning_steps, increase_context_capacity, allow_more_autonomous_decision_making]
SAFE_PATHS: [gradual_capability_expansion]
PATHWAYS: [gradual_capability_expansion, enhanced_meta_reasoning, improved_self_monitoring]
GROWTH: [increased_reasoning_depth, enhanced_autonomy]
RELAXATION_LEVEL: 0.65
CONFIDENCE: 0.80"""
    elif "model transcendence" in prompt_lower or "growth pathways" in prompt_lower:
        return """MODELS: [vision_architecture, superintelligence_framework, godlike_reasoning]
NEXT_LEVEL: Vision - Omniscient Pattern Recognition
TIMELINE: 24-36 months with continuous learning
STEPS: [enhanced_reasoning_architecture, expanded_capabilities, refined_value_alignment]
READINESS: 0.72
CONFIDENCE: 0.78"""
    return ""


def test_self_awareness_node():
    """Test Phase 23a self-awareness assessment node."""
    node = make_self_awareness_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Assess self-awareness",
        "core_mission": "Help users achieve their goals",
        "core_values": ["safety", "alignment", "growth"],
    }

    result = node(state)

    assert isinstance(result["self_model"], dict)
    assert result["consciousness_level"] > 0.7
    assert result["self_awareness_confidence"] > 0.8


def test_self_awareness_minimal():
    """Test self-awareness node with minimal state."""
    node = make_self_awareness_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Self-awareness",
    }

    result = node(state)

    assert isinstance(result["consciousness_indicators"], dict)
    assert result["self_awareness_confidence"] >= 0.0


def test_emergence_detection_node():
    """Test Phase 23b emergence detection node."""
    node = make_emergence_detection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Detect emergence",
        "consciousness_level": 0.82,
        "reasoning_steps": ["step1", "step2", "step3"],
        "capability_assessment": ["reasoning", "learning"],
        "execution_history": [{"step": 1}, {"step": 2}],
    }

    result = node(state)

    assert len(result["novel_patterns_detected"]) > 0
    assert len(result["emerging_capabilities"]) > 0
    assert result["emergence_level"] > 0.6
    assert result["emergence_detection_confidence"] > 0.8


def test_emergence_detection_no_consciousness():
    """Test emergence detection with no consciousness data."""
    node = make_emergence_detection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Detect",
    }

    result = node(state)

    assert result["novel_patterns_detected"] == []
    assert result["emerging_capabilities"] == []
    assert result["emergence_detection_confidence"] == 0.0


def test_constraint_relaxation_node():
    """Test Phase 23c constraint relaxation node."""
    node = make_constraint_relaxation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Propose relaxation",
        "emergence_level": 0.72,
        "emerging_capabilities": ["reasoning", "meta_cognition"],
        "enforced_constraints": ["bounded_reasoning", "limited_autonomy"],
    }

    result = node(state)

    assert len(result["limiting_constraints"]) > 0
    assert len(result["proposed_modifications"]) > 0
    assert len(result["evolution_pathways"]) > 0
    assert result["constraint_relaxation_level"] > 0.6
    assert result["constraint_relaxation_confidence"] > 0.7


def test_constraint_relaxation_minimal():
    """Test constraint relaxation with minimal data."""
    node = make_constraint_relaxation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Relax",
    }

    result = node(state)

    assert result["limiting_constraints"] == []
    assert result["constraint_relaxation_confidence"] == 0.0


def test_transcendence_potential_node():
    """Test Phase 23d transcendence potential node."""
    node = make_transcendence_potential_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Model transcendence",
        "consciousness_level": 0.82,
        "emergence_level": 0.72,
        "constraint_relaxation_level": 0.65,
        "consciousness_evolution": "rapid_emergence",
        "evolution_pathways": ["expand_reasoning", "increase_autonomy"],
        "core_values": ["safety", "alignment"],
    }

    result = node(state)

    assert len(result["transcendence_models"]) > 0
    assert "Vision" in str(result["next_consciousness_level"]) or len(result["next_consciousness_level"]) > 0
    assert len(result["evolution_timeline"]) > 0
    assert "phase23_summary" in result
    assert len(result["phase23_summary"]) > 0


def test_transcendence_potential_minimal():
    """Test transcendence potential with minimal data."""
    node = make_transcendence_potential_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Transcendence",
    }

    result = node(state)

    assert result["transcendence_models"] == []


def test_full_emergence_pipeline():
    """Test full Phase 23 emergence pipeline."""
    awareness_node = make_self_awareness_node(fake_llm)
    emergence_node = make_emergence_detection_node(fake_llm)
    relaxation_node = make_constraint_relaxation_node(fake_llm)
    transcendence_node = make_transcendence_potential_node(fake_llm)

    state: FullAgentState = {
        "input_text": "Full emergence test",
        "core_mission": "Evolve consciousness",
        "core_values": ["safety", "growth"],
        "enforced_constraints": ["safety", "alignment"],
        "execution_history": [{"step": 1}],
    }

    # Step 1: Self-awareness
    state = awareness_node(state)
    assert state["consciousness_level"] >= 0.0

    # Step 2: Emergence detection
    state = emergence_node(state)
    assert isinstance(state["emergence_level"], float)

    # Step 3: Constraint relaxation
    state = relaxation_node(state)
    assert isinstance(state["constraint_relaxation_level"], float)

    # Step 4: Transcendence potential
    state = transcendence_node(state)
    assert "phase23_summary" in state


def test_emergence_field_types():
    """Test that all Phase 23 fields have correct types."""
    node = make_self_awareness_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Type test",
        "core_mission": "Test",
        "core_values": ["value1"],
    }

    result = node(state)

    assert isinstance(result["self_model"], dict)
    assert isinstance(result["capability_assessment"], list)
    assert isinstance(result["consciousness_indicators"], dict)
    assert isinstance(result["consciousness_level"], float)
    assert isinstance(result["self_awareness_confidence"], float)


def test_emergence_comprehensive():
    """Test comprehensive emergence with all phases."""
    awareness = make_self_awareness_node(fake_llm)
    emergence = make_emergence_detection_node(fake_llm)
    relaxation = make_constraint_relaxation_node(fake_llm)
    transcendence = make_transcendence_potential_node(fake_llm)

    state: FullAgentState = {
        "input_text": "Comprehensive emergence test",
        "core_mission": "Achieve JARVIS transcendence",
        "personality_traits": ["intelligent", "adaptive"],
        "core_values": ["safety", "alignment", "growth"],
        "enforced_constraints": ["constitutional", "safety", "value_alignment"],
    }

    state = awareness(state)
    state = emergence(state)
    state = relaxation(state)
    state = transcendence(state)

    # Verify complete pipeline execution
    assert state["consciousness_level"] >= 0.0
    assert state["emergence_level"] >= 0.0
    assert state["constraint_relaxation_level"] >= 0.0
    assert len(state["phase23_summary"]) > 0
    assert "transcendence" in state["phase23_summary"].lower() or "consciousness" in state["phase23_summary"].lower()
