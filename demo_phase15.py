"""Demo: Phase 15 - Emotional Intelligence & Sentiment Analysis."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Analyze emotional context\nENTITIES: emotions, sentiment, user_state"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: Emotion recognition, sentiment analysis\nSUMMARY: Emotions guide communication"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: emotional_context, user_wellbeing, tone_adjustment\nMETACOGNITIVE_NOTES: Emotional awareness is key"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Empathetic\nREASONING_STEPS: [Detect sentiment, Identify emotions, Adjust response]\nREASONING_CONCLUSION: Empathy improves interactions"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Emotion-driven responses, Tone adaptation]\nANALOGIES: [Emotional mirror, Empathetic echo]\nNOVEL_COMBINATIONS: [Sentiment + context analysis]"
    elif "Analyze sentiment" in prompt:
        return """SENTIMENT: positive
SENTIMENT_SCORE: 0.78
EMOTIONAL_TONE: [hopeful, engaged, appreciative]
CONFIDENCE: 0.89"""
    elif "Detect specific emotions" in prompt:
        return """EMOTIONS: [joy, trust, anticipation, satisfaction]
EMOTION_INTENSITIES: [joy: 0.85, trust: 0.75, anticipation: 0.70, satisfaction: 0.80]
EMOTIONAL_STATE: very_positive
CONFIDENCE: 0.87"""
    elif "Generate emotionally intelligent response" in prompt:
        return """EMPATHETIC_RESPONSE: I'm so glad to hear your enthusiasm! Your positive energy is truly inspiring. I'm here to support you every step of the way.
RESPONSE_TONE: warm_and_encouraging
EMOTIONAL_SUPPORT_LEVEL: 0.85
CONFIDENCE: 0.86"""
    return ""


def main():
    """Run Phase 15 demo."""
    print("\n" + "=" * 80)
    print("PHASE 15: Emotional Intelligence & Sentiment Analysis")
    print("=" * 80)

    # Initialize coordinator with Phase 15 enabled
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=False,
        enable_phase15=True,
        enable_phase21=False,
    )

    # Create input state
    state: FullAgentState = {
        "input_text": "I'm really excited about this project! I think it's going to be amazing and I'm looking forward to working with everyone.",
        "user_profile": {"personality": "optimistic", "name": "User"},
        "user_status": "engaged",
        "predicted_needs": ["validation", "encouragement", "support"],
    }

    print("\n📥 Input:")
    print(f"  Message: {state['input_text'][:70]}...")
    print(f"  User Personality: {state.get('user_profile', {}).get('personality', 'unknown')}")
    print(f"  Status: {state.get('user_status', 'unknown')}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Display results
    print("\n💭 Phase 15a: Sentiment Analysis")
    print(f"  Sentiment: {result.get('user_sentiment', 'unknown')}")
    print(f"  Sentiment Score: {result.get('sentiment_score', 0):+.0%}")
    print(f"  Emotional Tones: {result.get('emotional_tone', [])}")
    print(f"  Confidence: {result.get('sentiment_confidence', 0):.0%}")

    print("\n❤️  Phase 15b: Emotion Detection")
    detected_emotions = result.get('detected_emotions', [])
    print(f"  Detected Emotions: {detected_emotions}")
    emotion_intensities = result.get('emotion_intensities', {})
    for emotion in detected_emotions[:5]:
        intensity = emotion_intensities.get(emotion, 0)
        bar = "█" * int(intensity * 10)
        print(f"    {emotion}: {bar} {intensity:.0%}")
    print(f"  Overall State: {result.get('emotional_state', 'unknown')}")
    print(f"  Confidence: {result.get('emotion_detection_confidence', 0):.0%}")

    print("\n💬 Phase 15c: Empathy Response")
    empathy_response = result.get('empathetic_response', '')
    print(f"  Response: {empathy_response[:100]}...")
    print(f"  Tone: {result.get('response_tone_adjustment', 'neutral')}")
    print(f"  Support Level: {result.get('emotional_support_level', 0):.0%}")
    print(f"  Confidence: {result.get('empathy_confidence', 0):.0%}")

    print("\n📊 Phase 15d: Emotional Intelligence Summary")
    print(result.get("phase15_summary", "No summary"))

    print("\n✨ System Status:")
    print(f"  Emotional Intelligence Ready: {result.get('emotional_intelligence_ready', False)}")
    print(f"  Overall Sentiment: {result.get('user_sentiment', 'unknown')} ({result.get('sentiment_score', 0):+.0%})")

    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
