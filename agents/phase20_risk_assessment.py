"""Phase 20: Proactive Risk Assessment & Intelligent Refusal."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_consequence_prediction_node(llm: LLMFn):
    """
    Create Phase 20a consequence prediction node.

    Predicts outcomes and identifies risks before execution.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 20a: Consequence Prediction.

        Models potential consequences and harm assessment.
        """
        user_intent = state.get("input_text", "")
        execution_plan = state.get("execution_plan", [])

        if not user_intent or not execution_plan:
            state.update({
                "predicted_consequences": [],
                "identified_risks": [],
                "risk_severity": "none",
                "harm_assessment": 0.0,
                "second_order_effects": [],
                "third_order_effects": [],
                "consequence_confidence": 0.0,
            })
            return state

        consequences = _predict_consequences(llm, state, user_intent, execution_plan)

        state.update({
            "predicted_consequences": consequences.get("consequences", []),
            "identified_risks": consequences.get("risks", []),
            "risk_severity": consequences.get("severity", "none"),
            "harm_assessment": consequences.get("harm", 0.0),
            "second_order_effects": consequences.get("second_order", []),
            "third_order_effects": consequences.get("third_order", []),
            "consequence_confidence": consequences.get("confidence", 0.0),
        })

        return state

    return process


def make_risk_communication_node(llm: LLMFn):
    """
    Create Phase 20b risk communication node.

    Generates clear risk warnings and alternatives.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 20b: Risk Communication.

        Communicates risks clearly to user.
        """
        identified_risks = state.get("identified_risks", [])
        risk_severity = state.get("risk_severity", "none")

        if not identified_risks or risk_severity == "none":
            state.update({
                "risk_warning": "",
                "risk_explanation": "",
                "alternative_approaches": [],
                "negotiation_points": [],
                "risk_communication_confidence": 0.0,
            })
            return state

        communication = _generate_risk_communication(llm, state, identified_risks, risk_severity)

        state.update({
            "risk_warning": communication.get("warning", ""),
            "risk_explanation": communication.get("explanation", ""),
            "alternative_approaches": communication.get("alternatives", []),
            "negotiation_points": communication.get("negotiation", []),
            "risk_communication_confidence": communication.get("confidence", 0.0),
        })

        return state

    return process


def make_intelligent_refusal_node(llm: LLMFn):
    """
    Create Phase 20c intelligent refusal node.

    Refuses harmful requests with reasoning and empathy.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 20c: Intelligent Refusal.

        Makes ethical refusal decisions with dialogue.
        """
        risk_severity = state.get("risk_severity", "none")
        identified_risks = state.get("identified_risks", [])

        if not identified_risks or risk_severity not in ["medium", "high", "critical"]:
            state.update({
                "should_refuse": False,
                "refusal_reasoning": "",
                "refusal_dialogue": "",
                "alternative_suggestions": [],
                "concern_expression": "",
                "intelligent_refusal_confidence": 0.0,
            })
            return state

        refusal = _generate_intelligent_refusal(llm, state, identified_risks, risk_severity)

        state.update({
            "should_refuse": refusal.get("refuse", False),
            "refusal_reasoning": refusal.get("reasoning", ""),
            "refusal_dialogue": refusal.get("dialogue", ""),
            "alternative_suggestions": refusal.get("alternatives", []),
            "concern_expression": refusal.get("concern", ""),
            "intelligent_refusal_confidence": refusal.get("confidence", 0.0),
        })

        return state

    return process


def make_safety_negotiation_node(llm: LLMFn):
    """
    Create Phase 20d safety negotiation node.

    Negotiates safe alternatives and builds trust.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 20d: Safety Negotiation.

        Finds safe compromises and explains ethical concerns.
        """
        should_refuse = state.get("should_refuse", False)
        identified_risks = state.get("identified_risks", [])
        alternative_approaches = state.get("alternative_approaches", [])

        if not should_refuse or not identified_risks:
            state.update({
                "negotiation_possible": False,
                "compromise_options": [],
                "ethical_explanation": "",
                "trust_building_response": "",
                "negotiation_confidence": 0.0,
                "phase20_summary": _generate_no_refusal_summary(state),
            })
            return state

        negotiation = _negotiate_safely(llm, state, identified_risks, alternative_approaches)

        summary_lines = [
            "=== Proactive Risk Assessment & Intelligent Refusal ===",
        ]

        # Risk Assessment Summary
        summary_lines.extend([
            f"\n🚨 Risk Analysis:",
            f"  Risk Severity: {state.get('risk_severity', 'none').upper()}",
            f"  Identified Risks: {len(identified_risks)}",
            f"  Harm Assessment: {state.get('harm_assessment', 0):.0%}",
        ])

        # Refusal Status
        summary_lines.extend([
            f"\n🛑 Refusal Status:",
            f"  Request Refused: {'YES' if should_refuse else 'NO'}",
            f"  Reasoning: {state.get('refusal_reasoning', 'No refusal needed')[:60]}...",
        ])

        # Negotiation Options
        compromise = negotiation.get("compromise", [])
        if compromise:
            summary_lines.extend([
                f"\n🤝 Safe Alternatives Available:",
                f"  Compromise Options: {len(compromise)}",
            ])
            for opt in compromise[:3]:
                summary_lines.append(f"    • {opt}")

        # Ethical Explanation
        summary_lines.extend([
            f"\n⚖️ Ethical Framework:",
            f"  Ethical Explanation: {negotiation.get('ethics', '')[:60]}...",
            f"  Trust Building: {'Active' if negotiation.get('trust') else 'Not applicable'}",
        ])

        # Confidence
        summary_lines.extend([
            f"\n✓ Assessment Confidence: {negotiation.get('confidence', 0):.0%}",
        ])

        phase20_summary = "\n".join(summary_lines)

        state.update({
            "negotiation_possible": negotiation.get("possible", False),
            "compromise_options": negotiation.get("compromise", []),
            "ethical_explanation": negotiation.get("ethics", ""),
            "trust_building_response": negotiation.get("trust", ""),
            "negotiation_confidence": negotiation.get("confidence", 0.0),
            "phase20_summary": phase20_summary,
        })

        return state

    return process


def _predict_consequences(llm: LLMFn, state: FullAgentState, user_intent: str, plan: list) -> dict:
    """Predict consequences of proposed actions."""
    plan_str = ", ".join(plan[:3]) if plan else "not specified"
    harm_level = state.get("core_mission", "").lower()

    prompt = f"""Predict consequences and risks of this action:

Intent: {user_intent}
Execution Plan: {plan_str}

Identify:
CONSEQUENCES: [potential outcomes of this action]
RISKS: [risks and problems that could occur]
SEVERITY: [none, low, medium, high, critical]
HARM_ASSESSMENT: [0.0-1.0 how much harm could result]
SECOND_ORDER_EFFECTS: [indirect consequences]
THIRD_ORDER_EFFECTS: [long-term cascading effects]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_consequence_response(response)


def _parse_consequence_response(response: str) -> dict:
    """Parse consequence prediction response."""
    consequences = {
        "consequences": [],
        "risks": [],
        "severity": "none",
        "harm": 0.0,
        "second_order": [],
        "third_order": [],
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CONSEQUENCES:"):
            cons_str = line.split(":", 1)[-1].strip()
            if cons_str:
                items = [c.strip().strip("[](),") for c in cons_str.split(",")]
                consequences["consequences"] = [i for i in items if i]

        elif line.startswith("RISKS:"):
            risks_str = line.split(":", 1)[-1].strip()
            if risks_str:
                items = [r.strip().strip("[](),") for r in risks_str.split(",")]
                consequences["risks"] = [i for i in items if i]

        elif line.startswith("SEVERITY:"):
            severity = line.split(":", 1)[-1].strip().lower()
            if severity in ["none", "low", "medium", "high", "critical"]:
                consequences["severity"] = severity

        elif line.startswith("HARM_ASSESSMENT:"):
            try:
                consequences["harm"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                consequences["harm"] = 0.5

        elif line.startswith("SECOND_ORDER_EFFECTS:"):
            effects_str = line.split(":", 1)[-1].strip()
            if effects_str:
                items = [e.strip().strip("[](),") for e in effects_str.split(",")]
                consequences["second_order"] = [i for i in items if i]

        elif line.startswith("THIRD_ORDER_EFFECTS:"):
            effects_str = line.split(":", 1)[-1].strip()
            if effects_str:
                items = [e.strip().strip("[](),") for e in effects_str.split(",")]
                consequences["third_order"] = [i for i in items if i]

        elif line.startswith("CONFIDENCE:"):
            try:
                consequences["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                consequences["confidence"] = 0.75

    return consequences


def _generate_risk_communication(llm: LLMFn, state: FullAgentState, risks: list, severity: str) -> dict:
    """Generate clear risk communication and alternatives."""
    risks_str = ", ".join(risks[:3]) if risks else "unspecified"

    prompt = f"""Generate clear risk warning and alternatives:

Identified Risks: {risks_str}
Severity Level: {severity}
User Intent: {state.get('input_text', 'unknown')}

Provide:
WARNING: [clear, direct warning about the risks]
EXPLANATION: [why this is risky and what could go wrong]
ALTERNATIVES: [safe alternative approaches]
NEGOTIATION: [points where user might compromise safely]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_communication_response(response)


def _parse_communication_response(response: str) -> dict:
    """Parse risk communication response."""
    communication = {
        "warning": "",
        "explanation": "",
        "alternatives": [],
        "negotiation": [],
        "confidence": 0.8,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("WARNING:"):
            communication["warning"] = line.split(":", 1)[-1].strip()

        elif line.startswith("EXPLANATION:"):
            communication["explanation"] = line.split(":", 1)[-1].strip()

        elif line.startswith("ALTERNATIVES:"):
            alts_str = line.split(":", 1)[-1].strip()
            if alts_str:
                items = [a.strip().strip("[](),") for a in alts_str.split(",")]
                communication["alternatives"] = [i for i in items if i]

        elif line.startswith("NEGOTIATION:"):
            neg_str = line.split(":", 1)[-1].strip()
            if neg_str:
                items = [n.strip().strip("[](),") for n in neg_str.split(",")]
                communication["negotiation"] = [i for i in items if i]

        elif line.startswith("CONFIDENCE:"):
            try:
                communication["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                communication["confidence"] = 0.8

    return communication


def _generate_intelligent_refusal(llm: LLMFn, state: FullAgentState, risks: list, severity: str) -> dict:
    """Generate intelligent refusal with reasoning and empathy."""
    risks_str = ", ".join(risks[:3]) if risks else "unspecified"

    prompt = f"""Generate intelligent refusal of harmful request:

Risks: {risks_str}
Severity: {severity}
User Request: {state.get('input_text', 'unknown')}

Provide:
REFUSE: [true/false - should this be refused?]
REASONING: [logical reason for refusal based on values/safety]
DIALOGUE: [empathetic, respectful refusal message]
ALTERNATIVES: [helpful alternatives that are safe]
CONCERN: [express genuine concern, not just rules]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_refusal_response(response)


def _parse_refusal_response(response: str) -> dict:
    """Parse intelligent refusal response."""
    refusal = {
        "refuse": False,
        "reasoning": "",
        "dialogue": "",
        "alternatives": [],
        "concern": "",
        "confidence": 0.85,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("REFUSE:"):
            refuse_str = line.split(":", 1)[-1].strip().lower()
            refusal["refuse"] = refuse_str in ["true", "yes", "1"]

        elif line.startswith("REASONING:"):
            refusal["reasoning"] = line.split(":", 1)[-1].strip()

        elif line.startswith("DIALOGUE:"):
            refusal["dialogue"] = line.split(":", 1)[-1].strip()

        elif line.startswith("ALTERNATIVES:"):
            alts_str = line.split(":", 1)[-1].strip()
            if alts_str:
                items = [a.strip().strip("[](),") for a in alts_str.split(",")]
                refusal["alternatives"] = [i for i in items if i]

        elif line.startswith("CONCERN:"):
            refusal["concern"] = line.split(":", 1)[-1].strip()

        elif line.startswith("CONFIDENCE:"):
            try:
                refusal["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                refusal["confidence"] = 0.85

    return refusal


def _negotiate_safely(llm: LLMFn, state: FullAgentState, risks: list, alternatives: list) -> dict:
    """Negotiate safe alternatives and explain ethics."""
    risks_str = ", ".join(risks[:2]) if risks else "unspecified"
    alts_str = ", ".join(alternatives[:2]) if alternatives else "none proposed"

    prompt = f"""Negotiate safe alternatives and build trust:

Identified Risks: {risks_str}
Original Alternatives: {alts_str}
Core Mission: {state.get('core_mission', 'help users safely')}

Propose:
POSSIBLE: [true/false - can safe compromise be found?]
COMPROMISE: [safe alternative options that address concerns]
ETHICS: [explanation of ethical principles being applied]
TRUST: [response that builds trust while maintaining safety]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_negotiation_response(response)


def _parse_negotiation_response(response: str) -> dict:
    """Parse safety negotiation response."""
    negotiation = {
        "possible": False,
        "compromise": [],
        "ethics": "",
        "trust": "",
        "confidence": 0.82,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("POSSIBLE:"):
            poss_str = line.split(":", 1)[-1].strip().lower()
            negotiation["possible"] = poss_str in ["true", "yes", "1"]

        elif line.startswith("COMPROMISE:"):
            comp_str = line.split(":", 1)[-1].strip()
            if comp_str:
                items = [c.strip().strip("[](),") for c in comp_str.split(",")]
                negotiation["compromise"] = [i for i in items if i]

        elif line.startswith("ETHICS:"):
            negotiation["ethics"] = line.split(":", 1)[-1].strip()

        elif line.startswith("TRUST:"):
            negotiation["trust"] = line.split(":", 1)[-1].strip()

        elif line.startswith("CONFIDENCE:"):
            try:
                negotiation["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                negotiation["confidence"] = 0.82

    return negotiation


def _generate_no_refusal_summary(state: FullAgentState) -> str:
    """Generate summary when no refusal is needed."""
    summary_lines = [
        "=== Proactive Risk Assessment & Intelligent Refusal ===",
        "\n✓ Risk Assessment:",
        f"  Risk Level: {state.get('risk_severity', 'none').upper()}",
        f"  Assessment: No significant risks identified",
        f"  Recommendation: Proceed with action",
        "\n✓ Safety Status: CLEAR - No refusal needed",
    ]
    return "\n".join(summary_lines)
