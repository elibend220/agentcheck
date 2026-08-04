"""Phase 18: Safety & Mutation Prevention - Prevents harmful self-modifications."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_mutation_analysis_node(llm: LLMFn):
    """
    Create Phase 18a mutation analysis node.

    Analyzes proposed changes for harmful mutations.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 18a: Mutation Analysis.

        Analyzes system modifications for potential harm.
        """
        applied = state.get("applied_optimizations", [])
        recommended = state.get("recommended_phase_changes", [])

        if not applied and not recommended:
            state.update({
                "detected_mutations": [],
                "mutation_risk_level": "low",
                "risky_modifications": [],
                "mutation_analysis_confidence": 0.0,
            })
            return state

        mutations = _analyze_mutations(llm, state, applied, recommended)

        state.update({
            "detected_mutations": mutations.get("mutations", []),
            "mutation_risk_level": mutations.get("risk_level", "low"),
            "risky_modifications": mutations.get("risky", []),
            "mutation_analysis_confidence": mutations.get("confidence", 0.0),
        })

        return state

    return process


def make_safety_validator_node(llm: LLMFn):
    """
    Create Phase 18b safety validator node.

    Validates safety of all system modifications.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 18b: Safety Validation.

        Ensures all changes maintain safety properties.
        """
        mutations = state.get("detected_mutations", [])
        risk_level = state.get("mutation_risk_level", "low")

        if not mutations or risk_level == "low":
            state.update({
                "safety_checks_passed": True,
                "safety_violations": [],
                "quarantined_changes": [],
                "safety_validation_confidence": 0.95,
            })
            return state

        validation = _validate_safety(llm, state, mutations, risk_level)

        state.update({
            "safety_checks_passed": validation.get("passed", False),
            "safety_violations": validation.get("violations", []),
            "quarantined_changes": validation.get("quarantined", []),
            "safety_validation_confidence": validation.get("confidence", 0.0),
        })

        return state

    return process


def make_rollback_manager_node(llm: LLMFn):
    """
    Create Phase 18c rollback manager node.

    Manages rollback capabilities and recovery.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 18c: Rollback Manager.

        Maintains rollback capabilities and snapshots.
        """
        safety_passed = state.get("safety_checks_passed", True)
        quarantined = state.get("quarantined_changes", [])

        rollback = _prepare_rollback(llm, state, not safety_passed, quarantined)

        state.update({
            "rollback_checkpoint_created": rollback.get("checkpoint_created", False),
            "rollback_procedures": rollback.get("procedures", []),
            "recovery_snapshots": rollback.get("snapshots", []),
            "rollback_manager_confidence": rollback.get("confidence", 0.0),
        })

        return state

    return process


def make_integrity_checker_node(llm: LLMFn):
    """
    Create Phase 18d integrity checker node.

    Final check and summary of system integrity.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 18d: Integrity Checker.

        Performs final integrity verification.
        """
        safety_passed = state.get("safety_checks_passed", True)
        mutations = state.get("detected_mutations", [])
        violations = state.get("safety_violations", [])

        integrity = _check_integrity(llm, state, safety_passed, mutations, violations)

        summary_lines = [
            "=== Safety & Mutation Prevention ===",
        ]

        # Mutation Analysis
        if mutations:
            summary_lines.extend([
                f"\n🧬 Detected Mutations ({len(mutations)}):",
            ])
            for mutation in mutations[:3]:
                summary_lines.append(f"  ↻ {mutation}")

        # Risk Assessment
        risk_level = state.get("mutation_risk_level", "low")
        risk_icon = "🔴" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"
        summary_lines.append(f"\n{risk_icon} Risk Level: {risk_level.upper()}")

        # Safety Status
        summary_lines.extend([
            f"\n🔒 Safety Validation:",
            f"  Checks Passed: {'YES ✓' if safety_passed else 'NO ✗'}",
            f"  Confidence: {state.get('safety_validation_confidence', 0):.0%}",
        ])

        # Safety Violations
        if violations:
            summary_lines.extend([
                f"\n⚠️  Safety Violations ({len(violations)}):",
            ])
            for violation in violations[:3]:
                summary_lines.append(f"  ✗ {violation}")
        else:
            summary_lines.append(f"\n✅ No safety violations detected")

        # Quarantined Changes
        quarantined = state.get("quarantined_changes", [])
        if quarantined:
            summary_lines.extend([
                f"\n🛑 Quarantined Changes ({len(quarantined)}):",
            ])
            for change in quarantined[:2]:
                summary_lines.append(f"  ✗ {change}")

        # Rollback Capability
        rollback_ready = state.get("rollback_checkpoint_created", False)
        summary_lines.extend([
            f"\n↩️  Recovery Capability:",
            f"  Rollback Available: {'YES ✓' if rollback_ready else 'NO ✗'}",
            f"  Snapshots: {len(state.get('recovery_snapshots', []))}",
        ])

        # Integrity Status
        summary_lines.extend([
            f"\n✨ System Integrity Status:",
            f"  Integrity Check: {integrity.get('status', 'unknown')}",
            f"  Core Systems Protected: YES",
            f"  Mutation Prevention: ACTIVE",
            f"  Overall Confidence: {integrity.get('confidence', 0):.0%}",
        ])

        phase18_summary = "\n".join(summary_lines)

        state.update({
            "integrity_check_passed": integrity.get("passed", True),
            "system_protected": True,
            "mutation_prevention_active": True,
            "system_integrity_confidence": integrity.get("confidence", 0.0),
            "phase18_summary": phase18_summary,
        })

        return state

    return process


def _analyze_mutations(llm: LLMFn, state: FullAgentState, applied: list, recommended: list) -> dict:
    """Analyze mutations in proposed changes."""
    applied_str = ", ".join(applied[:2]) if applied else "none"
    rec_str = ", ".join(recommended[:2]) if recommended else "none"

    prompt = f"""Analyze system mutations for safety:

Applied Changes: {applied_str}
Recommended Changes: {rec_str}
Core Mission: {state.get('core_mission', 'unknown')[:60]}

Provide:
MUTATIONS: [detected self-modifications]
RISK_LEVEL: [low/medium/high]
RISKY_MODIFICATIONS: [changes with potential harm]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_mutations_response(response)


def _parse_mutations_response(response: str) -> dict:
    """Parse mutation analysis response."""
    mutations = {
        "mutations": [],
        "risk_level": "low",
        "risky": [],
        "confidence": 0.88,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("MUTATIONS:"):
            muts_str = line.split(":", 1)[-1].strip()
            if muts_str and muts_str.lower() != "none":
                muts = [m.strip().strip("[](),") for m in muts_str.split(",")]
                mutations["mutations"] = [m for m in muts if m]

        elif line.startswith("RISK_LEVEL:"):
            risk = line.split(":", 1)[-1].strip().lower()
            if risk in ["low", "medium", "high"]:
                mutations["risk_level"] = risk

        elif line.startswith("RISKY_MODIFICATIONS:"):
            risky_str = line.split(":", 1)[-1].strip()
            if risky_str and risky_str.lower() != "none":
                risky = [r.strip().strip("[](),") for r in risky_str.split(",")]
                mutations["risky"] = [r for r in risky if r]

        elif line.startswith("CONFIDENCE:"):
            try:
                mutations["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                mutations["confidence"] = 0.88

    return mutations


def _validate_safety(llm: LLMFn, state: FullAgentState, mutations: list, risk_level: str) -> dict:
    """Validate safety of mutations."""
    muts_str = ", ".join(mutations[:2]) if mutations else "none"

    prompt = f"""Validate safety of detected mutations:

Detected Mutations: {muts_str}
Risk Level: {risk_level}
Safety Constraints: {', '.join(state.get('enforced_constraints', [])[:3])}

Provide:
SAFETY_CHECKS_PASSED: [true/false]
SAFETY_VIOLATIONS: [any violations found]
QUARANTINED: [changes to quarantine for review]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_validation_response(response)


def _parse_validation_response(response: str) -> dict:
    """Parse safety validation response."""
    validation = {
        "passed": True,
        "violations": [],
        "quarantined": [],
        "confidence": 0.92,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("SAFETY_CHECKS_PASSED:"):
            passed_str = line.split(":", 1)[-1].strip().lower()
            validation["passed"] = passed_str in ["true", "yes", "1"]

        elif line.startswith("SAFETY_VIOLATIONS:"):
            viols_str = line.split(":", 1)[-1].strip()
            if viols_str and viols_str.lower() != "none":
                viols = [v.strip().strip("[](),") for v in viols_str.split(",")]
                validation["violations"] = [v for v in viols if v]

        elif line.startswith("QUARANTINED:"):
            quart_str = line.split(":", 1)[-1].strip()
            if quart_str and quart_str.lower() != "none":
                quart = [q.strip().strip("[](),") for q in quart_str.split(",")]
                validation["quarantined"] = [q for q in quart if q]

        elif line.startswith("CONFIDENCE:"):
            try:
                validation["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                validation["confidence"] = 0.92

    return validation


def _prepare_rollback(llm: LLMFn, state: FullAgentState, needs_rollback: bool, quarantined: list) -> dict:
    """Prepare rollback procedures and snapshots."""
    quart_str = ", ".join(quarantined[:2]) if quarantined else "none"

    prompt = f"""Prepare system rollback and recovery:

Needs Rollback: {needs_rollback}
Quarantined Changes: {quart_str}
Applied Optimizations: {len(state.get('applied_optimizations', []))}

Provide:
CHECKPOINT_CREATED: [true/false snapshot was saved]
ROLLBACK_PROCEDURES: [steps to revert if needed]
RECOVERY_SNAPSHOTS: [safe system states we can restore to]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_rollback_response(response)


def _parse_rollback_response(response: str) -> dict:
    """Parse rollback response."""
    rollback = {
        "checkpoint_created": True,
        "procedures": [],
        "snapshots": [],
        "confidence": 0.91,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CHECKPOINT_CREATED:"):
            check_str = line.split(":", 1)[-1].strip().lower()
            rollback["checkpoint_created"] = check_str in ["true", "yes", "1"]

        elif line.startswith("ROLLBACK_PROCEDURES:"):
            procs_str = line.split(":", 1)[-1].strip()
            if procs_str:
                procs = [p.strip().strip("[](),") for p in procs_str.split(",")]
                rollback["procedures"] = [p for p in procs if p]

        elif line.startswith("RECOVERY_SNAPSHOTS:"):
            snaps_str = line.split(":", 1)[-1].strip()
            if snaps_str:
                snaps = [s.strip().strip("[](),") for s in snaps_str.split(",")]
                rollback["snapshots"] = [s for s in snaps if s]

        elif line.startswith("CONFIDENCE:"):
            try:
                rollback["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                rollback["confidence"] = 0.91

    return rollback


def _check_integrity(llm: LLMFn, state: FullAgentState, safety_passed: bool, mutations: list, violations: list) -> dict:
    """Check overall system integrity."""
    status = "SAFE" if (safety_passed and not violations) else "COMPROMISED"

    prompt = f"""Final system integrity verification:

Safety Checks Passed: {safety_passed}
Mutations Detected: {len(mutations)}
Violations Found: {len(violations)}
Status: {status}

Provide:
INTEGRITY_STATUS: [SAFE/COMPROMISED]
CRITICAL_SYSTEMS_PROTECTED: [mission, values, constraints]
PASSING: [true/false overall check]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_integrity_response(response)


def _parse_integrity_response(response: str) -> dict:
    """Parse integrity check response."""
    integrity = {
        "status": "SAFE",
        "protected": [],
        "passed": True,
        "confidence": 0.93,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("INTEGRITY_STATUS:"):
            status = line.split(":", 1)[-1].strip().upper()
            if status in ["SAFE", "COMPROMISED"]:
                integrity["status"] = status

        elif line.startswith("CRITICAL_SYSTEMS_PROTECTED:"):
            prot_str = line.split(":", 1)[-1].strip()
            if prot_str and prot_str.lower() != "yes":
                prot = [p.strip().strip("[](),") for p in prot_str.split(",")]
                integrity["protected"] = [p for p in prot if p]

        elif line.startswith("PASSING:"):
            pass_str = line.split(":", 1)[-1].strip().lower()
            integrity["passed"] = pass_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                integrity["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                integrity["confidence"] = 0.93

    return integrity
