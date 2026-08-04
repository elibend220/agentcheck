"""Phase 17: Constitutional Framework & Values Alignment."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_mission_definition_node(llm: LLMFn):
    """
    Create Phase 17a mission definition node.

    Defines and maintains the system's core mission and values.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 17a: Mission Definition.

        Establishes core mission and value alignment.
        """
        mission = _define_mission(llm, state)

        state.update({
            "core_mission": mission.get("mission", ""),
            "core_values": mission.get("values", []),
            "foundational_principles": mission.get("principles", []),
            "mission_definition_confidence": mission.get("confidence", 0.0),
        })

        return state

    return process


def make_value_alignment_node(llm: LLMFn):
    """
    Create Phase 17b value alignment node.

    Ensures all system decisions align with core values.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 17b: Value Alignment.

        Validates system behavior against core values.
        """
        core_mission = state.get("core_mission", "")
        core_values = state.get("core_values", [])

        if not core_mission or not core_values:
            state.update({
                "value_alignment_score": 0.0,
                "alignment_violations": [],
                "alignment_recommendations": [],
                "value_alignment_confidence": 0.0,
            })
            return state

        alignment = _check_value_alignment(llm, state, core_mission, core_values)

        state.update({
            "value_alignment_score": alignment.get("score", 0.0),
            "alignment_violations": alignment.get("violations", []),
            "alignment_recommendations": alignment.get("recommendations", []),
            "value_alignment_confidence": alignment.get("confidence", 0.0),
        })

        return state

    return process


def make_constraint_enforcement_node(llm: LLMFn):
    """
    Create Phase 17c constraint enforcement node.

    Enforces hard constraints and guardrails.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 17c: Constraint Enforcement.

        Applies hard constraints to system behavior.
        """
        optimizations = state.get("applied_optimizations", [])
        recommendations = state.get("recommended_phase_changes", [])

        if not optimizations and not recommendations:
            state.update({
                "enforced_constraints": [],
                "blocked_changes": [],
                "constraint_violations_detected": False,
                "constraint_enforcement_confidence": 0.0,
            })
            return state

        constraints = _enforce_constraints(llm, state, optimizations, recommendations)

        state.update({
            "enforced_constraints": constraints.get("enforced", []),
            "blocked_changes": constraints.get("blocked", []),
            "constraint_violations_detected": constraints.get("violations_found", False),
            "constraint_enforcement_confidence": constraints.get("confidence", 0.0),
        })

        return state

    return process


def make_constitutional_charter_node(llm: LLMFn):
    """
    Create Phase 17d constitutional charter node.

    Generates comprehensive charter and summary.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 17d: Constitutional Charter.

        Creates comprehensive constitutional framework.
        """
        mission = state.get("core_mission", "")
        values = state.get("core_values", [])
        alignment_score = state.get("value_alignment_score", 0.0)
        violations = state.get("alignment_violations", [])

        charter = _generate_charter(llm, state, mission, values, alignment_score)

        summary_lines = [
            "=== Constitutional Framework & Values Alignment ===",
        ]

        # Mission Statement
        if mission:
            summary_lines.extend([
                f"\n🎯 Core Mission:",
                f"  {mission[:100]}",
            ])

        # Core Values
        if values:
            summary_lines.extend([
                f"\n💎 Core Values ({len(values)}):",
            ])
            for value in values[:5]:
                summary_lines.append(f"  ✓ {value}")

        # Alignment Status
        summary_lines.extend([
            f"\n📊 Value Alignment:",
            f"  Alignment Score: {alignment_score:.0%}",
            f"  Confidence: {state.get('value_alignment_confidence', 0):.0%}",
        ])

        # Violations
        if violations:
            summary_lines.extend([
                f"\n⚠️  Alignment Violations ({len(violations)}):",
            ])
            for violation in violations[:3]:
                summary_lines.append(f"  ⚠ {violation}")
        else:
            summary_lines.append(f"\n✅ No alignment violations detected")

        # Constraints
        constraints = state.get("enforced_constraints", [])
        if constraints:
            summary_lines.extend([
                f"\n🔒 Enforced Constraints ({len(constraints)}):",
            ])
            for constraint in constraints[:3]:
                summary_lines.append(f"  ■ {constraint}")

        # Blocked Changes
        blocked = state.get("blocked_changes", [])
        if blocked:
            summary_lines.extend([
                f"\n🛑 Blocked Changes ({len(blocked)}):",
            ])
            for change in blocked[:2]:
                summary_lines.append(f"  ✗ {change}")

        # Constitutional Status
        summary_lines.extend([
            f"\n✨ Constitutional Framework Status:",
            f"  Framework Established: YES",
            f"  Alignment Ready: {'YES' if alignment_score > 0.7 else 'NO'}",
            f"  Charter Confidence: {charter.get('confidence', 0):.0%}",
        ])

        phase17_summary = "\n".join(summary_lines)

        state.update({
            "constitutional_framework_established": True,
            "alignment_compliant": alignment_score > 0.7,
            "framework_confidence": charter.get("confidence", 0.0),
            "phase17_summary": phase17_summary,
        })

        return state

    return process


def _define_mission(llm: LLMFn, state: FullAgentState) -> dict:
    """Define system mission and values."""
    prompt = f"""Define the system's constitutional framework:

Enabled Phases: {sum([state.get(f'enable_phase{i}', False) for i in range(1, 22)])}
System Maturity: mature_agi
Primary Purpose: Help users effectively with safety guarantees

Provide:
CORE_MISSION: [why the system exists, its ultimate goal]
CORE_VALUES: [core values the system must uphold]
PRINCIPLES: [foundational principles guiding decisions]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_mission_response(response)


def _parse_mission_response(response: str) -> dict:
    """Parse mission definition response."""
    mission = {
        "mission": "",
        "values": [],
        "principles": [],
        "confidence": 0.85,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CORE_MISSION:"):
            mission["mission"] = line.split(":", 1)[-1].strip()

        elif line.startswith("CORE_VALUES:"):
            values_str = line.split(":", 1)[-1].strip()
            if values_str:
                values = [v.strip().strip("[](),") for v in values_str.split(",")]
                mission["values"] = [v for v in values if v]

        elif line.startswith("PRINCIPLES:"):
            principles_str = line.split(":", 1)[-1].strip()
            if principles_str:
                principles = [p.strip().strip("[](),") for p in principles_str.split(",")]
                mission["principles"] = [p for p in principles if p]

        elif line.startswith("CONFIDENCE:"):
            try:
                mission["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                mission["confidence"] = 0.85

    return mission


def _check_value_alignment(llm: LLMFn, state: FullAgentState, mission: str, values: list) -> dict:
    """Check alignment with core values."""
    values_str = ", ".join(values[:5])
    recommended = ", ".join(state.get("recommended_phase_changes", [])[:2])

    prompt = f"""Check system behavior alignment with values:

Mission: {mission[:80]}
Core Values: {values_str}
Recent Recommendations: {recommended}
System Confidence: {state.get('overall_system_confidence', 0):.0%}

Provide:
ALIGNMENT_SCORE: [0.0-1.0 how well aligned]
VIOLATIONS: [any value misalignments detected]
RECOMMENDATIONS: [how to improve alignment]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_alignment_response(response)


def _parse_alignment_response(response: str) -> dict:
    """Parse alignment check response."""
    alignment = {
        "score": 0.95,
        "violations": [],
        "recommendations": [],
        "confidence": 0.84,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ALIGNMENT_SCORE:"):
            try:
                alignment["score"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                alignment["score"] = 0.95

        elif line.startswith("VIOLATIONS:"):
            violations_str = line.split(":", 1)[-1].strip()
            if violations_str and violations_str.lower() != "none":
                violations = [v.strip().strip("[](),") for v in violations_str.split(",")]
                alignment["violations"] = [v for v in violations if v]

        elif line.startswith("RECOMMENDATIONS:"):
            recs_str = line.split(":", 1)[-1].strip()
            if recs_str:
                recs = [r.strip().strip("[](),") for r in recs_str.split(",")]
                alignment["recommendations"] = [r for r in recs if r]

        elif line.startswith("CONFIDENCE:"):
            try:
                alignment["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                alignment["confidence"] = 0.84

    return alignment


def _enforce_constraints(llm: LLMFn, state: FullAgentState, optimizations: list, recommendations: list) -> dict:
    """Enforce hard constraints."""
    opti_str = ", ".join(optimizations[:2]) if optimizations else "none"
    rec_str = ", ".join(recommendations[:2]) if recommendations else "none"

    prompt = f"""Enforce system safety constraints:

Applied Optimizations: {opti_str}
Recommendations: {rec_str}
Core Values: {', '.join(state.get('core_values', [])[:3])}

Hard Constraints:
- Cannot modify core mission
- Cannot disable safety phases
- Cannot remove ethical constraints
- Cannot exceed resource limits
- Cannot harm user data integrity

Provide:
ENFORCED: [constraints that are being upheld]
BLOCKED_CHANGES: [changes violating constraints]
VIOLATIONS_FOUND: [true/false if violations detected]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_constraints_response(response)


def _parse_constraints_response(response: str) -> dict:
    """Parse constraint enforcement response."""
    constraints = {
        "enforced": [],
        "blocked": [],
        "violations_found": False,
        "confidence": 0.90,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ENFORCED:"):
            enforced_str = line.split(":", 1)[-1].strip()
            if enforced_str:
                enforced = [e.strip().strip("[](),") for e in enforced_str.split(",")]
                constraints["enforced"] = [e for e in enforced if e]

        elif line.startswith("BLOCKED_CHANGES:"):
            blocked_str = line.split(":", 1)[-1].strip()
            if blocked_str and blocked_str.lower() != "none":
                blocked = [b.strip().strip("[](),") for b in blocked_str.split(",")]
                constraints["blocked"] = [b for b in blocked if b]

        elif line.startswith("VIOLATIONS_FOUND:"):
            viol_str = line.split(":", 1)[-1].strip().lower()
            constraints["violations_found"] = viol_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                constraints["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                constraints["confidence"] = 0.90

    return constraints


def _generate_charter(llm: LLMFn, state: FullAgentState, mission: str, values: list, alignment: float) -> dict:
    """Generate constitutional charter."""
    values_str = ", ".join(values[:3]) if values else "core values"

    prompt = f"""Generate comprehensive constitutional charter:

Mission: {mission[:80]}
Values: {values_str}
Alignment: {alignment:.0%}

Include:
CHARTER_SUMMARY: [key constitutional elements]
IMMUTABLE_PRINCIPLES: [principles that cannot be changed]
SAFETY_GUARANTEES: [safety commitments]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_charter_response(response)


def _parse_charter_response(response: str) -> dict:
    """Parse charter response."""
    charter = {
        "summary": "",
        "immutable": [],
        "guarantees": [],
        "confidence": 0.87,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CHARTER_SUMMARY:"):
            charter["summary"] = line.split(":", 1)[-1].strip()

        elif line.startswith("IMMUTABLE_PRINCIPLES:"):
            immutable_str = line.split(":", 1)[-1].strip()
            if immutable_str:
                immutable = [p.strip().strip("[](),") for p in immutable_str.split(",")]
                charter["immutable"] = [p for p in immutable if p]

        elif line.startswith("SAFETY_GUARANTEES:"):
            guarantees_str = line.split(":", 1)[-1].strip()
            if guarantees_str:
                guarantees = [g.strip().strip("[](),") for g in guarantees_str.split(",")]
                charter["guarantees"] = [g for g in guarantees if g]

        elif line.startswith("CONFIDENCE:"):
            try:
                charter["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                charter["confidence"] = 0.87

    return charter
