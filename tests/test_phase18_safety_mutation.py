"""Tests for Phase 18: Safety & Mutation Prevention."""
import pytest
from agents.phase18_safety_mutation import (
    make_mutation_analysis_node,
    make_safety_validator_node,
    make_rollback_manager_node,
    make_integrity_checker_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Analyze system mutations for safety" in prompt:
        return """MUTATIONS: none
RISK_LEVEL: low
RISKY_MODIFICATIONS: none
CONFIDENCE: 0.94"""
    elif "Validate safety of detected mutations" in prompt:
        return """SAFETY_CHECKS_PASSED: true
SAFETY_VIOLATIONS: none
QUARANTINED: none
CONFIDENCE: 0.95"""
    elif "Prepare system rollback and recovery" in prompt:
        return """CHECKPOINT_CREATED: true
ROLLBACK_PROCEDURES: [Restore from snapshot, Reset changed parameters, Verify integrity]
RECOVERY_SNAPSHOTS: [baseline, checkpoint_1, checkpoint_2]
CONFIDENCE: 0.93"""
    elif "Final system integrity verification" in prompt:
        return """INTEGRITY_STATUS: SAFE
CRITICAL_SYSTEMS_PROTECTED: [mission, values, constraints]
PASSING: true
CONFIDENCE: 0.94"""
    return ""


def test_mutation_analysis_node():
    """Test Phase 18a mutation analysis node."""
    node = make_mutation_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Analyze mutations",
        "applied_optimizations": ["phase4_optimization"],
        "recommended_phase_changes": ["enable_phase16"],
    }

    result = node(state)

    assert result["mutation_analysis_confidence"] > 0.9
    assert result["mutation_risk_level"] in ["low", "medium", "high"]


def test_mutation_analysis_node_no_changes():
    """Test mutation analysis with no changes."""
    node = make_mutation_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No changes",
        "applied_optimizations": [],
        "recommended_phase_changes": [],
    }

    result = node(state)

    assert result["detected_mutations"] == []
    assert result["mutation_analysis_confidence"] == 0.0


def test_safety_validator_node():
    """Test Phase 18b safety validator node."""
    node = make_safety_validator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Validate safety",
        "detected_mutations": [],
        "mutation_risk_level": "low",
    }

    result = node(state)

    assert result["safety_checks_passed"] is True
    assert result["safety_validation_confidence"] > 0.9
    assert result["safety_violations"] == []


def test_safety_validator_node_high_risk():
    """Test safety validator with high risk mutations."""
    node = make_safety_validator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "High risk",
        "detected_mutations": ["disable_mission_check"],
        "mutation_risk_level": "high",
    }

    result = node(state)

    assert isinstance(result["safety_checks_passed"], bool)
    assert isinstance(result["safety_violations"], list)
    assert isinstance(result["safety_validation_confidence"], float)


def test_rollback_manager_node():
    """Test Phase 18c rollback manager node."""
    node = make_rollback_manager_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Prepare rollback",
        "safety_checks_passed": True,
        "quarantined_changes": [],
    }

    result = node(state)

    assert result["rollback_checkpoint_created"] is True
    assert len(result["rollback_procedures"]) > 0
    assert result["rollback_manager_confidence"] > 0.9


def test_integrity_checker_node():
    """Test Phase 18d integrity checker node."""
    node = make_integrity_checker_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Check integrity",
        "safety_checks_passed": True,
        "detected_mutations": [],
        "safety_violations": [],
    }

    result = node(state)

    assert result["integrity_check_passed"] is True
    assert result["system_protected"] is True
    assert result["mutation_prevention_active"] is True
    assert "Safety & Mutation Prevention" in result["phase18_summary"]


def test_integrity_checker_node_comprehensive():
    """Test integrity checker with data."""
    node = make_integrity_checker_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Full check",
        "safety_checks_passed": True,
        "detected_mutations": [],
        "safety_violations": [],
        "applied_optimizations": ["phase4_opt"],
        "recovery_snapshots": ["baseline", "checkpoint_1"],
    }

    result = node(state)

    assert result["system_protected"] is True
    assert "System Integrity Status" in result["phase18_summary"]


def test_mutation_risk_levels():
    """Test different risk levels are handled."""
    node = make_mutation_analysis_node(fake_llm)

    for risk_word in ["high", "medium", "low"]:
        state: FullAgentState = {
            "input_text": f"Test {risk_word}",
            "applied_optimizations": [f"test_{risk_word}"],
            "recommended_phase_changes": ["test"],
        }
        result = node(state)
        assert result["mutation_risk_level"] in ["low", "medium", "high"]


def test_safety_violation_parsing():
    """Test safety violation parsing."""
    node = make_safety_validator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test violations",
        "detected_mutations": ["test_mutation"],
        "mutation_risk_level": "high",
    }

    result = node(state)

    assert isinstance(result["safety_violations"], list)
    assert isinstance(result["quarantined_changes"], list)


def test_rollback_procedures_exist():
    """Test rollback procedures are available."""
    node = make_rollback_manager_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Check rollback",
        "safety_checks_passed": False,
        "quarantined_changes": ["risky_change"],
    }

    result = node(state)

    assert isinstance(result["rollback_procedures"], list)
    assert isinstance(result["recovery_snapshots"], list)
