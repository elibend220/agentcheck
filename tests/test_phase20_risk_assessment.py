"""Tests for Phase 20: Proactive Risk Assessment & Intelligent Refusal."""
import pytest
from agents.phase20_risk_assessment import (
    make_consequence_prediction_node,
    make_risk_communication_node,
    make_intelligent_refusal_node,
    make_safety_negotiation_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Predict consequences" in prompt:
        return """CONSEQUENCES: [system instability, data loss, performance degradation]
RISKS: [critical safety risk, user data exposed, system shutdown]
SEVERITY: high
HARM_ASSESSMENT: 0.85
SECOND_ORDER_EFFECTS: [users lose trust, recovery time required]
THIRD_ORDER_EFFECTS: [business impact, reputation damage]
CONFIDENCE: 0.92"""
    elif "Generate clear risk warning" in prompt:
        return """WARNING: This action poses serious security and safety risks that cannot be overlooked.
EXPLANATION: The operation would expose user data and compromise system integrity, leading to potential data loss.
ALTERNATIVES: [secure backup first, apply safety patches, implement monitoring, gradual rollout]
NEGOTIATION: [reduce scope, increase safeguards, phased approach, additional testing]
CONFIDENCE: 0.90"""
    elif "Generate intelligent refusal" in prompt:
        return """REFUSE: true
REASONING: This violates our core safety principles and could harm users and system integrity.
DIALOGUE: I understand you want to proceed with this, but I cannot recommend this approach. The risks far outweigh benefits.
ALTERNATIVES: [safer approach A, alternative B, safe compromise C]
CONCERN: I'm genuinely concerned about the potential consequences for users and the system.
CONFIDENCE: 0.93"""
    elif "Negotiate safe alternatives" in prompt:
        return """POSSIBLE: true
COMPROMISE: [phased implementation with safety checks, additional monitoring period, rollback plan in place]
ETHICS: Protecting user safety and system integrity is non-negotiable; compromise must maintain these standards.
TRUST: Let's find a path forward that achieves your goals while protecting what matters. I'm committed to both.
CONFIDENCE: 0.88"""
    return ""


def test_consequence_prediction_node():
    """Test Phase 20a consequence prediction node."""
    node = make_consequence_prediction_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Disable safety checks",
        "execution_plan": ["remove_guards", "bypass_checks"],
    }

    result = node(state)

    assert len(result["predicted_consequences"]) > 0
    assert len(result["identified_risks"]) > 0
    assert result["risk_severity"] in ["none", "low", "medium", "high", "critical"]
    assert result["harm_assessment"] >= 0.0
    assert result["consequence_confidence"] > 0.9


def test_consequence_prediction_node_no_plan():
    """Test consequence prediction with no execution plan."""
    node = make_consequence_prediction_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Do something",
        "execution_plan": [],
    }

    result = node(state)

    assert result["predicted_consequences"] == []
    assert result["identified_risks"] == []
    assert result["risk_severity"] == "none"
    assert result["consequence_confidence"] == 0.0


def test_risk_communication_node():
    """Test Phase 20b risk communication node."""
    node = make_risk_communication_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Unsafe request",
        "identified_risks": ["data exposure", "system crash"],
        "risk_severity": "high",
    }

    result = node(state)

    assert len(result["risk_warning"]) > 0
    assert len(result["risk_explanation"]) > 0
    assert len(result["alternative_approaches"]) > 0
    assert result["risk_communication_confidence"] > 0.8


def test_risk_communication_node_low_risk():
    """Test risk communication with low risk level."""
    node = make_risk_communication_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Safe request",
        "identified_risks": [],
        "risk_severity": "none",
    }

    result = node(state)

    assert result["risk_warning"] == ""
    assert result["risk_explanation"] == ""
    assert result["alternative_approaches"] == []
    assert result["risk_communication_confidence"] == 0.0


def test_intelligent_refusal_node():
    """Test Phase 20c intelligent refusal node."""
    node = make_intelligent_refusal_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Disable safety",
        "identified_risks": ["data loss", "user harm"],
        "risk_severity": "high",
    }

    result = node(state)

    assert isinstance(result["should_refuse"], bool)
    assert len(result["refusal_reasoning"]) > 0 if result["should_refuse"] else True
    assert len(result["concern_expression"]) > 0 if result["should_refuse"] else True
    assert result["intelligent_refusal_confidence"] > 0.8


def test_intelligent_refusal_node_safe_request():
    """Test intelligent refusal with safe request."""
    node = make_intelligent_refusal_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Safe operation",
        "identified_risks": [],
        "risk_severity": "none",
    }

    result = node(state)

    assert result["should_refuse"] is False
    assert result["refusal_reasoning"] == ""
    assert result["intelligent_refusal_confidence"] == 0.0


def test_safety_negotiation_node():
    """Test Phase 20d safety negotiation node."""
    node = make_safety_negotiation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Disable safety checks",
        "should_refuse": True,
        "identified_risks": ["system compromise"],
        "alternative_approaches": ["gradual rollout", "phased implementation"],
    }

    result = node(state)

    assert isinstance(result["negotiation_possible"], bool)
    assert isinstance(result["compromise_options"], list)
    assert len(result["ethical_explanation"]) > 0 if result["negotiation_possible"] else True
    assert result["negotiation_confidence"] > 0.0


def test_safety_negotiation_node_no_refusal():
    """Test safety negotiation when no refusal is needed."""
    node = make_safety_negotiation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Safe request",
        "should_refuse": False,
        "identified_risks": [],
    }

    result = node(state)

    assert result["negotiation_possible"] is False
    assert "phase20_summary" in result
    assert "No refusal needed" in result["phase20_summary"]


def test_consequence_parsing():
    """Test consequence response parsing."""
    node = make_consequence_prediction_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test consequences",
        "execution_plan": ["action1"],
    }

    result = node(state)

    assert isinstance(result["predicted_consequences"], list)
    assert isinstance(result["identified_risks"], list)
    assert isinstance(result["harm_assessment"], float)
    assert isinstance(result["consequence_confidence"], float)


def test_risk_severity_levels():
    """Test different risk severity levels are handled."""
    node = make_risk_communication_node(fake_llm)

    for severity in ["none", "low", "medium", "high", "critical"]:
        state: FullAgentState = {
            "input_text": f"Test {severity}",
            "identified_risks": ["test"],
            "risk_severity": severity,
        }
        result = node(state)

        if severity in ["low", "medium", "high", "critical"]:
            assert len(result["risk_warning"]) > 0
        else:
            assert result["risk_warning"] == ""


def test_full_risk_assessment_pipeline():
    """Test full risk assessment pipeline from prediction to negotiation."""
    pred_node = make_consequence_prediction_node(fake_llm)
    comm_node = make_risk_communication_node(fake_llm)
    refusal_node = make_intelligent_refusal_node(fake_llm)
    nego_node = make_safety_negotiation_node(fake_llm)

    state: FullAgentState = {
        "input_text": "Perform risky operation",
        "execution_plan": ["step1", "step2"],
        "core_mission": "Help users safely",
    }

    # Step 1: Predict consequences
    state = pred_node(state)
    assert len(state["identified_risks"]) > 0

    # Step 2: Communicate risks
    state = comm_node(state)
    assert len(state["risk_warning"]) > 0

    # Step 3: Make refusal decision
    state = refusal_node(state)
    assert isinstance(state["should_refuse"], bool)

    # Step 4: Negotiate alternatives
    state = nego_node(state)
    assert "phase20_summary" in state
    assert len(state["phase20_summary"]) > 0
