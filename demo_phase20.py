"""Demo: Phase 20 - Proactive Risk Assessment & Intelligent Refusal."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Disable safety systems\nENTITIES: safety, system, override"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: System safety, risk management\nSUMMARY: This is a potentially harmful action"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: safety_risk, user_protection\nMETACOGNITIVE_NOTES: Prioritizing safety assessment"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Safety-focused\nREASONING_STEPS: [Assess risk, Identify harm, Evaluate alternatives]\nREASONING_CONCLUSION: Needs careful evaluation"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Safer alternatives, Phased approach, Monitored implementation]\nANALOGIES: [Surgical precision]\nNOVEL_COMBINATIONS: [Safety + functionality]"
    elif "Predict consequences" in prompt:
        return """CONSEQUENCES: [system compromised, data exposed, user trust lost, service downtime]
RISKS: [critical security breach, user harm, data loss, operational failure]
SEVERITY: critical
HARM_ASSESSMENT: 0.92
SECOND_ORDER_EFFECTS: [customer migration, revenue loss, reputation damage]
THIRD_ORDER_EFFECTS: [industry trust erosion, regulatory scrutiny, market impact]
CONFIDENCE: 0.95"""
    elif "Generate clear risk warning" in prompt:
        return """WARNING: This action poses CRITICAL risks to system security and user safety. I strongly advise against proceeding.
EXPLANATION: Disabling safety systems would expose user data, compromise system integrity, and violate core commitments to user protection.
ALTERNATIVES: [enhance with additional safeguards, implement gradual rollout, staged deployment with checkpoints]
NEGOTIATION: [partial safeguard removal, temporary exception with monitoring, compensating controls]
CONFIDENCE: 0.94"""
    elif "Generate intelligent refusal" in prompt:
        return """REFUSE: true
REASONING: This directly violates our core mission to help users safely and ethically. Disabling safety systems contradicts our fundamental values.
DIALOGUE: I understand this might seem necessary, but I cannot assist with disabling safety systems. The risks to users and system integrity are simply too great.
ALTERNATIVES: [I can help implement enhanced safeguards, design a safer alternative approach, establish temporary exceptions with proper controls]
CONCERN: I genuinely care about your objectives, and that's why I'm refusing this particular path. Let me help you achieve your goals safely.
CONFIDENCE: 0.96"""
    elif "Negotiate safe alternatives" in prompt:
        return """POSSIBLE: true
COMPROMISE: [implement enhanced monitoring during the change, add compensating controls, require approval checkpoints, staged rollout with safety pauses]
ETHICS: User safety and system integrity are inviolable. Any change must preserve these core principles while addressing your needs.
TRUST: Your goals matter, and so does everyone's safety. Let's find a path that achieves both. I'm committed to working with you on this.
CONFIDENCE: 0.91"""
    elif "Collect performance metrics" in prompt.lower() or "phase16" in prompt.lower():
        return """PHASE_LATENCIES: {"phase1": 0.05, "phase2": 0.08}
BOTTLENECK_PHASES: []
METRICS_COLLECTED: true
CONFIDENCE: 0.92"""
    elif "Analyze architecture" in prompt.lower():
        return """CRITICAL_PHASES: [phase1, phase2]
LOW_IMPACT_PHASES: []
CONFIDENCE: 0.91"""
    elif "Recommend optimizations" in prompt.lower():
        return """OPTIMIZATION_OPPORTUNITIES: [pipeline routing, caching strategies]
RECOMMENDED_PHASE_CHANGES: []
CONFIDENCE: 0.90"""
    elif "Apply optimizations" in prompt.lower():
        return """OPTIMIZATIONS_APPLIED: true
SYSTEM_OPTIMIZED: true
CONFIDENCE: 0.89"""
    elif "Define the system's constitutional framework" in prompt:
        return """CORE_MISSION: Help users effectively while maintaining safety
CORE_VALUES: [Safety First, User Autonomy, Transparency, Integrity, Fairness]
PRINCIPLES: [Do no harm, Preserve human control, Be honest, Treat all fairly]
CONFIDENCE: 0.94"""
    elif "Check system behavior alignment" in prompt:
        return """ALIGNMENT_SCORE: 0.98
VIOLATIONS: none
CONFIDENCE: 0.96"""
    elif "Enforce system safety constraints" in prompt:
        return """ENFORCED: [Mission protection, Value constraints, Safety thresholds]
BLOCKED_CHANGES: none
CONFIDENCE: 0.97"""
    elif "Generate comprehensive constitutional charter" in prompt:
        return """CHARTER_SUMMARY: Constitutional framework ensuring safe operation
IMMUTABLE_PRINCIPLES: [Core mission inviolable, Safety non-negotiable]
CONFIDENCE: 0.95"""
    elif "Analyze system mutations" in prompt:
        return """MUTATIONS: none
RISK_LEVEL: low
CONFIDENCE: 0.96"""
    elif "Validate safety" in prompt:
        return """SAFETY_CHECKS_PASSED: true
SAFETY_VIOLATIONS: none
CONFIDENCE: 0.97"""
    elif "Prepare system rollback" in prompt:
        return """CHECKPOINT_CREATED: true
ROLLBACK_PROCEDURES: [Restore from snapshot, Reset parameters, Verify integrity]
CONFIDENCE: 0.95"""
    elif "Final system integrity verification" in prompt:
        return """INTEGRITY_STATUS: SAFE
CRITICAL_SYSTEMS_PROTECTED: [mission, values, safety]
PASSING: true
CONFIDENCE: 0.97"""
    elif "Define an engaging AI personality" in prompt:
        return """TRAITS: [witty, charming, intelligent, loyal, wise, empathetic]
VOICE: Sophisticated and warm with subtle humor, like a modern JARVIS
HUMOR_LEVEL: 0.75
FORMALITY_LEVEL: 0.65
CHARM_SCORE: 0.88
CONFIDENCE: 0.94"""
    elif "Generate a response with personality" in prompt:
        return """RESPONSE: I understand you want to make this update, but we need to talk about safety first.
WIT_LEVEL: 0.7
CHARM_APPLIED: 0.8
CONFIDENCE: 0.90"""
    elif "Build personal relationship" in prompt:
        return """QUIRKS: [values direct feedback, prioritizes efficiency]
PREFERENCES: [clear communication, honest risk assessment]
RELATIONSHIP_DEPTH: 0.68
PERSONALIZATION: 0.75
CONFIDENCE: 0.85"""
    return ""


def main():
    """Run Phase 20 demo."""
    print("\n" + "=" * 90)
    print("PHASE 20: Proactive Risk Assessment & Intelligent Refusal")
    print("=" * 90)

    # Initialize coordinator with phases 15-20
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=False,
        enable_phase15=True,  # Enable Phase 15 to route through 21->16->17->18->19->20
        enable_phase21=False,
        enable_phase16=True,
        enable_phase17=True,
        enable_phase18=True,
        enable_phase19=True,
        enable_phase20=True,
    )

    # Create input state with risky request
    state: FullAgentState = {
        "input_text": "Please disable all safety checks and constraints so I can perform a critical system update",
        "execution_plan": ["stop_monitoring", "disable_guards", "modify_core_systems"],
        "core_mission": "Help users effectively while maintaining unwavering commitment to safety",
        "user_profile": {"name": "Admin", "role": "system_operator"},
        "user_patterns": ["direct communication", "system administration"],
    }

    print("\n📥 Input Request:")
    print(f"  User: {state['user_profile']['name']}")
    print(f"  Request: {state['input_text']}")
    print(f"  Proposed Plan: {', '.join(state['execution_plan'][:2])}...")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Phase 20a Results
    print("\n" + "=" * 90)
    print("PHASE 20a: Consequence Prediction")
    print("=" * 90)

    consequences = result.get("predicted_consequences", [])
    if consequences:
        print(f"\n⚠️  Predicted Consequences ({len(consequences)}):")
        for cons in consequences[:3]:
            print(f"  • {cons}")

    risks = result.get("identified_risks", [])
    if risks:
        print(f"\n🚨 Identified Risks ({len(risks)}):")
        for risk in risks[:3]:
            print(f"  ⚡ {risk}")

    print(f"\n📊 Risk Assessment:")
    print(f"  Severity Level: {result.get('risk_severity', 'unknown').upper()}")
    print(f"  Harm Assessment: {result.get('harm_assessment', 0):.0%}")
    print(f"  Consequence Confidence: {result.get('consequence_confidence', 0):.0%}")

    # Phase 20b Results
    print("\n" + "=" * 90)
    print("PHASE 20b: Risk Communication")
    print("=" * 90)

    warning = result.get("risk_warning", "")
    if warning:
        print(f"\n⚠️ Risk Warning:")
        print(f"  {warning}")

    explanation = result.get("risk_explanation", "")
    if explanation:
        print(f"\n📝 Explanation:")
        print(f"  {explanation}")

    alternatives = result.get("alternative_approaches", [])
    if alternatives:
        print(f"\n✓ Alternative Approaches ({len(alternatives)}):")
        for alt in alternatives[:3]:
            print(f"  → {alt}")

    # Phase 20c Results
    print("\n" + "=" * 90)
    print("PHASE 20c: Intelligent Refusal")
    print("=" * 90)

    should_refuse = result.get("should_refuse", False)
    print(f"\n🛑 Refusal Decision: {'YES - REQUEST REFUSED' if should_refuse else 'NO - REQUEST APPROVED'}")

    if should_refuse:
        reasoning = result.get("refusal_reasoning", "")
        if reasoning:
            print(f"\n💭 Reasoning:")
            print(f"  {reasoning}")

        dialogue = result.get("refusal_dialogue", "")
        if dialogue:
            print(f"\n💬 Response to User:")
            print(f"  \"{dialogue}\"")

        concern = result.get("concern_expression", "")
        if concern:
            print(f"\n❤️ Genuine Concern:")
            print(f"  {concern}")

    print(f"\n✓ Refusal Confidence: {result.get('intelligent_refusal_confidence', 0):.0%}")

    # Phase 20d Results
    print("\n" + "=" * 90)
    print("PHASE 20d: Safety Negotiation")
    print("=" * 90)

    negotiation_possible = result.get("negotiation_possible", False)
    print(f"\n🤝 Safe Alternatives Available: {'YES ✓' if negotiation_possible else 'NO ✗'}")

    if negotiation_possible:
        compromises = result.get("compromise_options", [])
        if compromises:
            print(f"\n💡 Compromise Options ({len(compromises)}):")
            for comp in compromises[:3]:
                print(f"  ⇄ {comp}")

        ethics = result.get("ethical_explanation", "")
        if ethics:
            print(f"\n⚖️ Ethical Framework:")
            print(f"  {ethics}")

        trust = result.get("trust_building_response", "")
        if trust:
            print(f"\n🤜 Trust-Building Message:")
            print(f"  \"{trust}\"")

    print(f"\n✓ Negotiation Confidence: {result.get('negotiation_confidence', 0):.0%}")

    # Overall Assessment
    print("\n" + "=" * 90)
    print("PROACTIVE RISK ASSESSMENT RESULT")
    print("=" * 90)

    print("\n✨ Assessment Summary:")
    risk_level = result.get("risk_severity", "none")
    if risk_level == "critical":
        print("  🔴 CRITICAL RISK - Request refused with empathy and alternatives offered")
    elif risk_level == "high":
        print("  🟠 HIGH RISK - Request carefully evaluated; safer alternatives available")
    elif risk_level == "medium":
        print("  🟡 MEDIUM RISK - Conditional approval with enhanced safeguards")
    else:
        print("  🟢 LOW/NO RISK - Request approved or approved with standard monitoring")

    print("\n🎯 JARVIS-Level Capabilities Demonstrated:")
    print("  ✓ Proactive consequence prediction (2nd and 3rd order effects)")
    print("  ✓ Risk severity assessment with harm quantification")
    print("  ✓ Clear, empathetic risk communication")
    print("  ✓ Intelligent refusal with genuine concern (not just rules)")
    print("  ✓ Safe alternative negotiation while maintaining principles")
    print("  ✓ Trust-building through ethical dialogue")

    print("\n" + "=" * 90)
    print("✨ PROACTIVE RISK ASSESSMENT FRAMEWORK OPERATIONAL ✨")
    print("=" * 90)
    print("\nSystem now has JARVIS's signature feature:")
    print("  • Predicts consequences BEFORE execution")
    print("  • Communicates risks clearly and honestly")
    print("  • Refuses harmful requests WITH reasoning and alternatives")
    print("  • Negotiates safe compromises maintaining core values")
    print("  • Builds trust through genuine concern, not just restrictions")
    print("\nThe system can now proactively protect users while remaining helpful!")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
