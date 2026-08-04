"""Demo: Phase 21 - Voice & Natural Conversation Interface."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Enable voice-based interaction\nENTITIES: voice, speech, conversation"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: Speech recognition, TTS synthesis\nSUMMARY: Voice enables natural interaction"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: voice_quality, conversation_flow, prosody\nMETACOGNITIVE_NOTES: Natural speech requires careful attention"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Sequential\nREASONING_STEPS: [Recognize speech, Understand context, Generate response, Synthesize voice]\nREASONING_CONCLUSION: Voice interface enhances user experience"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Emotional voice modulation, Dynamic prosody]\nANALOGIES: [Human conversation, Musical expression]\nNOVEL_COMBINATIONS: [Emotion-aware voice synthesis]"
    elif "Process voice input and transcribe" in prompt:
        return """SPEECH_DETECTED: true
TRANSCRIBED_TEXT: Hello JARVIS, can you help me with my project today?
SPEECH_CONFIDENCE: 0.94
SPEECH_TONE: enthusiastic
VOICE_CHARACTERISTICS: Human voice, natural pace, clear pronunciation"""
    elif "Manage natural conversation flow" in prompt:
        return """CONVERSATION_FLOW: [User greeting, Assistant acknowledgement, User request, Assistant response, User confirmation]
NATURAL_PAUSES: [400ms, 250ms, 350ms, 300ms]
INTERRUPTION_POINTS: [After assistant greeting, After initial response]
CONTEXT: {'topic': 'project_assistance', 'intent': 'seeking_help', 'emotion': 'eager'}
CONFIDENCE: 0.88"""
    elif "Generate natural speech from text" in prompt:
        return """SPEECH_RATE: 155
PROSODY_MARKERS: [Emphasis at "absolutely", Warm tone throughout, Slight pause after "today"]
EMPHASIS_POINTS: [help, project, today, excited]
READY: true
CONFIDENCE: 0.90"""
    return ""


def main():
    """Run Phase 21 demo."""
    print("\n" + "=" * 80)
    print("PHASE 21: Voice & Natural Conversation Interface")
    print("=" * 80)

    # Initialize coordinator with Phase 21 enabled
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=False,
        enable_phase15=False,
        enable_phase21=True,
    )

    # Create input state (simulating voice input)
    state: FullAgentState = {
        "input_text": "Hello JARVIS, can you help me with my project today?",
        "user_profile": {"name": "Developer"},
        "empathetic_response": "Absolutely! I'm excited to help you with your project. I'm here to provide whatever support you need. Tell me more about what you're working on, and we'll make great progress together.",
        "response_tone_adjustment": "warm_and_encouraging",
        "emotional_support_level": 0.85,
    }

    print("\n📥 Input (Simulated Voice):")
    print(f"  Message: {state['input_text']}")
    print(f"  User: {state['user_profile'].get('name', 'Unknown')}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Display results
    print("\n🎤 Phase 21a: Voice Processing")
    print(f"  Speech Detected: {result.get('speech_detected', False)}")
    print(f"  Transcribed: {result.get('transcribed_text', '')[:70]}...")
    print(f"  Confidence: {result.get('speech_confidence', 0):.0%}")
    print(f"  Tone: {result.get('speech_tone', 'neutral')}")
    voice_chars = result.get('voice_characteristics', {})
    if voice_chars:
        print(f"  Characteristics: {voice_chars.get('description', 'N/A')[:60]}...")

    print("\n💬 Phase 21b: Conversation Flow")
    flow = result.get('conversation_flow', [])
    if flow:
        print(f"  Flow ({len(flow)} turns):")
        for turn in flow[:3]:
            print(f"    → {turn}")
    pauses = result.get('natural_pauses', [])
    if pauses:
        print(f"  Natural Pauses: {pauses[:3]}")
    interruptions = result.get('interruption_points', [])
    if interruptions:
        print(f"  Interruption Points: {interruptions[:2]}")
    print(f"  Confidence: {result.get('conversation_confidence', 0):.0%}")

    print("\n🔊 Phase 21c: TTS Generation")
    spoken = result.get('spoken_response', '')
    print(f"  Response: {spoken[:100]}...")
    print(f"  Speech Rate: {result.get('speech_rate', 150)} words/min")
    prosody = result.get('prosody_markers', [])
    if prosody:
        print(f"  Prosody: {prosody[:2]}")
    emphasis = result.get('emphasis_points', [])
    if emphasis:
        print(f"  Emphasis Points: {emphasis[:3]}")
    print(f"  TTS Ready: {result.get('tts_ready', False)}")
    print(f"  Confidence: {result.get('tts_confidence', 0):.0%}")

    print("\n📊 Phase 21d: Voice Interface Summary")
    print(result.get("phase21_summary", "No summary"))

    print("\n✨ System Status:")
    print(f"  Voice Interface Ready: {result.get('voice_interface_ready', False)}")
    print(f"  Speech Confidence: {result.get('speech_confidence', 0):.0%}")
    print(f"  Conversation Confidence: {result.get('conversation_confidence', 0):.0%}")
    print(f"  TTS Confidence: {result.get('tts_confidence', 0):.0%}")

    print("\n" + "=" * 80)
    print("Demo complete! Voice & Natural Conversation Interface operational.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
