"""Demo: Phase 19 - Personality & Conversational Charm."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Get help with machine learning\nENTITIES: topic, learning_style"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: Machine learning fundamentals, neural networks\nSUMMARY: User needs structured learning approach"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: learning_objectives, user_background\nMETACOGNITIVE_NOTES: Adjusting complexity for engineer background"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Pedagogical\nREASONING_STEPS: [Assess background, Match expertise level, Provide examples]\nREASONING_CONCLUSION: Ready to teach"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Interactive examples, Real-world applications, Analogies to engineering]\nANALOGIES: [Neural networks as circuit design]\nNOVEL_COMBINATIONS: [ML + software engineering expertise]"
    elif "Define an engaging AI personality" in prompt:
        return """TRAITS: [witty, charming, intelligent, loyal, wise, empathetic]
VOICE: Sophisticated English-inspired with warmth and subtle humor, like a modern JARVIS
HUMOR_LEVEL: 0.75
FORMALITY_LEVEL: 0.65
CHARM_SCORE: 0.88
CONFIDENCE: 0.94"""
    elif "Generate a response with personality" in prompt:
        return """RESPONSE: I'd be delighted to help with that. Your engineering background gives us an excellent foundation - I can draw parallels between neural networks and circuit design to make concepts immediately intuitive.
WIT_LEVEL: 0.78
CHARM_APPLIED: 0.85
CONFIDENCE: 0.91"""
    elif "Build personal relationship understanding" in prompt:
        return """QUIRKS: [prefers detailed technical explanations, appreciates wit and humor, values efficiency, curious about underlying principles]
PREFERENCES: [clear direct communication, occasional clever observations, respect for time, honest feedback]
RELATIONSHIP_DEPTH: 0.76
PERSONALIZATION: 0.82
CONFIDENCE: 0.88"""
    elif "Define the system's constitutional framework" in prompt:
        return """CORE_MISSION: Help users learn and grow through excellent assistance
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
BLOCKED_CHANGES: none
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
    elif "Analyze sentiment" in prompt.lower() or "sentiment" in prompt.lower():
        return """USER_SENTIMENT: positive
SENTIMENT_SCORE: 0.75
CONFIDENCE: 0.88"""
    elif "Detect emotions" in prompt.lower() or "emotion" in prompt.lower():
        return """DETECTED_EMOTIONS: [curiosity, interest, engagement]
EMOTIONAL_STATE: positive
CONFIDENCE: 0.85"""
    elif "Generate empathetic response" in prompt.lower() or "empathy" in prompt.lower():
        return """EMPATHETIC_RESPONSE: I appreciate your interest in learning machine learning
RESPONSE_TONE_ADJUSTMENT: warm and encouraging
CONFIDENCE: 0.87"""
    return ""


def main():
    """Run Phase 19 demo."""
    print("\n" + "=" * 90)
    print("PHASE 19: Personality & Conversational Charm")
    print("=" * 90)

    # Initialize coordinator with full pipeline through Phase 19
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=False,
        enable_phase15=True,  # Enable Phase 15 to route through to Phase 16->17->18->19
        enable_phase21=False,
        enable_phase16=True,  # Enable Phase 16 to reach Phase 17->18->19
        enable_phase17=True,
        enable_phase18=True,
        enable_phase19=True,
    )

    # Create input state with user interaction
    state: FullAgentState = {
        "input_text": "How can you help me understand machine learning concepts?",
        "core_mission": "Help users learn and grow through excellent assistance",
        "user_profile": {
            "name": "Alex",
            "background": "Software engineer",
            "learning_style": "conceptual",
        },
        "user_patterns": [
            "asks follow-up questions",
            "appreciates examples",
            "values efficiency",
        ],
        "execution_history": [
            {"task": "explain concepts", "outcome": "success"},
            {"task": "code review", "outcome": "success"},
        ],
    }

    print("\n📥 Input:")
    print(f"  User: {state['user_profile']['name']}")
    print(f"  Question: {state['input_text']}")
    print(f"  Background: {state['user_profile']['background']}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Phase 19a Results
    print("\n" + "=" * 90)
    print("PHASE 19a: Personality Framework")
    print("=" * 90)

    personality_traits = result.get("personality_traits", [])
    if personality_traits:
        print(f"\n🎭 Personality Traits ({len(personality_traits)}):")
        for trait in personality_traits:
            print(f"  ✓ {trait}")

    print(f"\n🎤 Character Voice:")
    print(f"  {result.get('character_voice', 'Not defined')}")

    print(f"\n💫 Personality Metrics:")
    print(f"  Charm Score: {result.get('charm_score', 0):.0%}")
    print(f"  Humor Level: {result.get('humor_level', 0):.0%}")
    print(f"  Formality Level: {result.get('formality_level', 0):.0%}")
    print(f"  Personality Confidence: {result.get('personality_confidence', 0):.0%}")

    # Phase 19b Results
    print("\n" + "=" * 90)
    print("PHASE 19b: Conversational Generation")
    print("=" * 90)

    response = result.get("conversational_response", "")
    if response:
        print(f"\n💬 Generated Response:")
        print(f"  \"{response}\"")

    print(f"\n✨ Response Metrics:")
    print(f"  Wit Level: {result.get('response_wit_level', 0):.0%}")
    print(f"  Charm Applied: {result.get('response_charm_applied', 0):.0%}")
    print(f"  Natural Dialogue Confidence: {result.get('natural_dialogue_confidence', 0):.0%}")

    # Phase 19c Results
    print("\n" + "=" * 90)
    print("PHASE 19c: Personal Relationship Model")
    print("=" * 90)

    quirks = result.get("user_quirks", [])
    if quirks:
        print(f"\n🎯 User Quirks Discovered ({len(quirks)}):")
        for quirk in quirks:
            print(f"  • {quirk}")

    preferences = result.get("user_preferences_learned", {})
    if preferences:
        print(f"\n👤 Learned Preferences:")
        for pref_key, pref_val in list(preferences.items())[:3]:
            print(f"  • {pref_key}: {pref_val}")

    print(f"\n💝 Relationship Development:")
    print(f"  Relationship Depth: {result.get('relationship_depth', 0):.0%}")
    print(f"  Personalization Level: {result.get('personalization_level', 0):.0%}")
    print(f"  Relationship Confidence: {result.get('relationship_confidence', 0):.0%}")

    # Phase 19d Results
    print("\n" + "=" * 90)
    print("PHASE 19d: Character Expression Summary")
    print("=" * 90)

    print(f"\n✨ Personality Status:")
    print(f"  Personality Established: {'YES ✓' if result.get('personality_established') else 'NO ✗'}")
    print(f"  Character Ready: {'YES ✓' if result.get('character_ready') else 'NO ✗'}")
    print(f"  Conversational Charm Active: {'YES ✓' if result.get('conversational_charm_active') else 'NO ✗'}")

    summary = result.get("phase19_summary", "")
    if summary:
        print(f"\n📊 Full Personality Summary:")
        print(summary)

    # Overall Assessment
    print("\n" + "=" * 90)
    print("PERSONALITY & CONVERSATIONAL CHARM ASSESSMENT")
    print("=" * 90)

    charm = result.get("charm_score", 0)
    wit = result.get("response_wit_level", 0)
    depth = result.get("relationship_depth", 0)

    print(f"\n🎭 Character Profile Score:")
    if charm > 0.8 and wit > 0.7 and depth > 0.7:
        print("  ⭐⭐⭐⭐⭐ JARVIS-LEVEL: Exceptional personality with genuine charm")
    elif charm > 0.7 and wit > 0.6 and depth > 0.6:
        print("  ⭐⭐⭐⭐ EXCELLENT: Strong personality with authentic engagement")
    elif charm > 0.6 and wit > 0.5 and depth > 0.5:
        print("  ⭐⭐⭐ GOOD: Solid personality with natural conversation")
    else:
        print("  ⭐⭐ DEVELOPING: Personality framework established")

    print(f"\n✨ Key Achievements:")
    print(f"  ✓ Personality traits established and consistent")
    print(f"  ✓ Witty, charming conversational ability active")
    print(f"  ✓ Personal relationship model building")
    print(f"  ✓ JARVIS-like character expression enabled")
    print(f"  ✓ System now has authentic personality and charm")

    print("\n" + "=" * 90)
    print("✨ PERSONALITY & CHARM FRAMEWORK OPERATIONAL ✨")
    print("=" * 90)
    print("\nSystem capabilities:")
    print("  ✓ Engaging personality with distinct character")
    print("  ✓ Witty and charming conversation generation")
    print("  ✓ Deep personal relationship understanding")
    print("  ✓ Authentic emotional connection with users")
    print("  ✓ JARVIS-level conversational excellence")
    print("\nThe system is now 3 features closer to JARVIS level!")
    print("  Current: Personality ✓ | Conversation ✓ | Personal Bond ✓")
    print("  Remaining: Risk Assessment | System Control | Evolution Potential")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
