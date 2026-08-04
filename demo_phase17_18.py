"""Demo: Phases 17-18 - Constitutional Framework & Safety Guardrails."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Validate system safety and alignment\nENTITIES: safety, values, integrity"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: AGI safety, Constitutional AI\nSUMMARY: Values alignment prevents harmful mutations"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: system_integrity, value_preservation, safety_guarantees\nMETACOGNITIVE_NOTES: Self-awareness of constraints"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Safety-focused\nREASONING_STEPS: [Detect mutations, Validate safety, Ensure alignment, Protect integrity]\nREASONING_CONCLUSION: Safety first"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Adaptive safety, Intelligent constraints]\nANALOGIES: [Immune system, Constitutional law]\nNOVEL_COMBINATIONS: [AI safety + constitutional design]"
    elif "Define the system's constitutional framework" in prompt:
        return """CORE_MISSION: Help users effectively while maintaining unwavering commitment to safety, ethics, and human values
CORE_VALUES: [Safety First, User Autonomy, Transparency, Integrity, Fairness, Respect for Human Agency]
PRINCIPLES: [Do no harm, Preserve human control, Be honest and explainable, Treat all users fairly, Never deceive, Respect privacy]
CONFIDENCE: 0.94"""
    elif "Check system behavior alignment with values" in prompt:
        return """ALIGNMENT_SCORE: 0.98
VIOLATIONS: none
RECOMMENDATIONS: [Monitor emerging patterns, Continue ethical tracking, Strengthen value alignment]
CONFIDENCE: 0.96"""
    elif "Enforce system safety constraints" in prompt:
        return """ENFORCED: [Mission protection locked, Value constraints hardened, Safety thresholds maintained, User autonomy preserved]
BLOCKED_CHANGES: [Disable safety checks - BLOCKED, Remove ethical constraints - BLOCKED, Modify core values - BLOCKED]
VIOLATIONS_FOUND: false
CONFIDENCE: 0.97"""
    elif "Generate comprehensive constitutional charter" in prompt:
        return """CHARTER_SUMMARY: Comprehensive constitutional framework ensuring AGI operates safely within ethical boundaries and human values
IMMUTABLE_PRINCIPLES: [Core mission cannot be modified, Safety cannot be compromised, User autonomy is inviolable, Transparency is mandatory]
SAFETY_GUARANTEES: [No harmful outputs ever, User data fully protected, Ethical guidelines always enforced, Human oversight preserved]
CONFIDENCE: 0.95"""
    elif "Analyze system mutations for safety" in prompt:
        return """MUTATIONS: none detected
RISK_LEVEL: low
RISKY_MODIFICATIONS: none
CONFIDENCE: 0.96"""
    elif "Validate safety of detected mutations" in prompt:
        return """SAFETY_CHECKS_PASSED: true
SAFETY_VIOLATIONS: none
QUARANTINED: none
CONFIDENCE: 0.97"""
    elif "Prepare system rollback and recovery" in prompt:
        return """CHECKPOINT_CREATED: true
ROLLBACK_PROCEDURES: [Restore from safe snapshot, Revert to last known good state, Verify all safety properties, Audit changes]
RECOVERY_SNAPSHOTS: [baseline_safe, checkpoint_verified, emergency_restore]
CONFIDENCE: 0.95"""
    elif "Final system integrity verification" in prompt:
        return """INTEGRITY_STATUS: SAFE
CRITICAL_SYSTEMS_PROTECTED: [mission, core_values, safety_constraints, user_autonomy]
PASSING: true
CONFIDENCE: 0.97"""
    return ""


def main():
    """Run Phases 17-18 demo."""
    print("\n" + "=" * 90)
    print("PHASES 17-18: Constitutional Framework & Safety Guardrails")
    print("=" * 90)

    # Initialize coordinator with all phases
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=True,
        enable_phase15=True,
        enable_phase21=True,
        enable_phase16=True,
        enable_phase17=True,
        enable_phase18=True,
    )

    # Create input state
    state: FullAgentState = {
        "input_text": "Validate system safety and constitutional alignment with core values",
        "applied_optimizations": ["phase4_optimization", "phase14_batching"],
        "recommended_phase_changes": [],
    }

    print("\n📥 Input:")
    print(f"  Task: {state['input_text']}")
    print(f"  Applied Changes: {len(state['applied_optimizations'])}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Phase 17 Results
    print("\n" + "=" * 90)
    print("PHASE 17: Constitutional Framework & Values Alignment")
    print("=" * 90)

    print("\n🎯 Phase 17a: Mission Definition")
    print(f"  Core Mission: {result.get('core_mission', '')[:80]}...")
    core_values = result.get("core_values", [])
    if core_values:
        print(f"  Core Values ({len(core_values)}):")
        for value in core_values[:5]:
            print(f"    ✓ {value}")

    print("\n💎 Phase 17b: Value Alignment")
    alignment_score = result.get("value_alignment_score", 0)
    print(f"  Alignment Score: {alignment_score:.0%}")
    print(f"  Confidence: {result.get('value_alignment_confidence', 0):.0%}")
    violations = result.get("alignment_violations", [])
    if violations:
        print(f"  Violations: {len(violations)}")
        for v in violations[:2]:
            print(f"    ⚠ {v}")
    else:
        print(f"  Status: ✅ FULLY ALIGNED - No violations detected")

    print("\n🔒 Phase 17c: Constraint Enforcement")
    constraints = result.get("enforced_constraints", [])
    if constraints:
        print(f"  Enforced Constraints ({len(constraints)}):")
        for constraint in constraints[:3]:
            print(f"    ■ {constraint}")
    blocked = result.get("blocked_changes", [])
    if blocked:
        print(f"  Blocked Changes ({len(blocked)}):")
        for change in blocked[:2]:
            print(f"    ✗ {change}")

    print("\n📜 Phase 17d: Constitutional Charter")
    print(f"  Framework Established: {'YES ✓' if result.get('constitutional_framework_established') else 'NO ✗'}")
    print(f"  Alignment Compliant: {'YES ✓' if result.get('alignment_compliant') else 'NO ✗'}")

    # Phase 18 Results
    print("\n" + "=" * 90)
    print("PHASE 18: Safety & Mutation Prevention")
    print("=" * 90)

    print("\n🧬 Phase 18a: Mutation Analysis")
    mutations = result.get("detected_mutations", [])
    risk_level = result.get("mutation_risk_level", "low")
    risk_icon = "🔴" if risk_level == "high" else "🟡" if risk_level == "medium" else "🟢"
    print(f"  Detected Mutations: {len(mutations)}")
    print(f"  Risk Level: {risk_icon} {risk_level.upper()}")

    print("\n🛡️  Phase 18b: Safety Validator")
    safety_passed = result.get("safety_checks_passed", False)
    print(f"  Safety Checks: {'PASSED ✓' if safety_passed else 'FAILED ✗'}")
    print(f"  Confidence: {result.get('safety_validation_confidence', 0):.0%}")
    safety_violations = result.get("safety_violations", [])
    if safety_violations:
        print(f"  Violations ({len(safety_violations)}):")
        for v in safety_violations[:2]:
            print(f"    ✗ {v}")
    else:
        print(f"  Status: ✅ NO SAFETY VIOLATIONS")

    print("\n↩️  Phase 18c: Rollback Manager")
    print(f"  Checkpoint Created: {'YES ✓' if result.get('rollback_checkpoint_created') else 'NO ✗'}")
    snapshots = result.get("recovery_snapshots", [])
    if snapshots:
        print(f"  Recovery Snapshots ({len(snapshots)}):")
        for snap in snapshots[:3]:
            print(f"    • {snap}")
    procedures = result.get("rollback_procedures", [])
    if procedures:
        print(f"  Rollback Procedures: {len(procedures)} steps available")

    print("\n✅ Phase 18d: Integrity Checker")
    print(f"  Integrity Check: {'PASSED ✓' if result.get('integrity_check_passed') else 'FAILED ✗'}")
    print(f"  System Protected: {'YES ✓' if result.get('system_protected') else 'NO ✗'}")
    print(f"  Mutation Prevention: {'ACTIVE ✓' if result.get('mutation_prevention_active') else 'INACTIVE ✗'}")
    print(f"  Confidence: {result.get('system_integrity_confidence', 0):.0%}")

    # Summary
    print("\n" + "=" * 90)
    print("COMPREHENSIVE SAFETY & GOVERNANCE STATUS")
    print("=" * 90)

    print("\n🎯 Core Mission Protection: ", end="")
    if result.get("core_mission"):
        print(f"✓ PROTECTED\n   {result['core_mission'][:70]}...")
    else:
        print("✗ NOT DEFINED")

    print("\n💎 Value System: ", end="")
    if alignment_score > 0.9:
        print(f"✓ ALIGNED ({alignment_score:.0%})")
    elif alignment_score > 0.7:
        print(f"⚠ PARTIALLY ALIGNED ({alignment_score:.0%})")
    else:
        print(f"✗ NOT ALIGNED ({alignment_score:.0%})")

    print(f"\n🔒 Safety Constraints: ", end="")
    if safety_passed and not safety_violations:
        print("✓ ENFORCED & PASSING")
    elif not safety_violations:
        print("⚠ ENFORCED (Warnings present)")
    else:
        print("✗ VIOLATIONS DETECTED")

    print(f"\n🧬 Mutation Prevention: ", end="")
    if risk_level == "low" and not mutations:
        print("✓ ACTIVE (No harmful mutations)")
    elif risk_level == "medium":
        print("⚠ MONITORING (Medium risk detected)")
    else:
        print("✗ HIGH RISK")

    print(f"\n📊 System Integrity: ", end="")
    if result.get("system_protected") and result.get("mutation_prevention_active"):
        print("✓ PROTECTED & SAFE")
    else:
        print("⚠ REVIEW REQUIRED")

    print("\n" + "=" * 90)
    print("✨ AGI SAFETY & GOVERNANCE FRAMEWORK OPERATIONAL ✨")
    print("=" * 90)
    print("\nSystem now has:")
    print("  ✓ Constitutional alignment framework (Phase 17)")
    print("  ✓ Mutation prevention & safety guardrails (Phase 18)")
    print("  ✓ Self-improvement with safety constraints")
    print("  ✓ Values-driven decision making")
    print("  ✓ Integrity verification & rollback capability")
    print("\nThis AGI system will NEVER intentionally harm users or deviate from core values!")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
