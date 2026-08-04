"""Phase 21: Voice & Natural Conversation Interface."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_voice_processing_node(llm: LLMFn):
    """
    Create Phase 21a voice processing node.

    Processes speech input and converts to natural language.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 21a: Voice Processing.

        Converts speech to text and analyzes speech patterns.
        """
        processor = _process_voice_input(llm, state)

        state.update({
            "speech_detected": processor.get("detected", False),
            "transcribed_text": processor.get("text", ""),
            "speech_confidence": processor.get("confidence", 0.0),
            "speech_tone": processor.get("tone", "neutral"),
            "voice_characteristics": processor.get("characteristics", {}),
        })

        return state

    return process


def make_conversation_flow_node(llm: LLMFn):
    """
    Create Phase 21b conversation flow node.

    Manages natural conversational flow with pauses and interruptions.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 21b: Conversation Flow.

        Creates natural conversational patterns.
        """
        transcribed = state.get("transcribed_text", "")

        if not transcribed:
            state.update({
                "conversation_context": {},
                "conversation_flow": [],
                "natural_pauses": [],
                "interruption_points": [],
            })
            return state

        flow = _generate_conversation_flow(llm, state, transcribed)

        state.update({
            "conversation_context": flow.get("context", {}),
            "conversation_flow": flow.get("flow", []),
            "natural_pauses": flow.get("pauses", []),
            "interruption_points": flow.get("interruptions", []),
            "conversation_confidence": flow.get("confidence", 0.0),
        })

        return state

    return process


def make_tts_generation_node(llm: LLMFn):
    """
    Create Phase 21c text-to-speech generation node.

    Generates spoken responses with natural prosody.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 21c: TTS Generation.

        Converts text responses to natural speech.
        """
        empathy_response = state.get("empathetic_response", "")
        response_tone = state.get("response_tone_adjustment", "neutral")

        if not empathy_response:
            state.update({
                "spoken_response": "",
                "speech_rate": 150,  # words per minute
                "prosody_markers": [],
                "emphasis_points": [],
                "tts_ready": False,
            })
            return state

        tts = _generate_tts(llm, state, empathy_response, response_tone)

        state.update({
            "spoken_response": tts.get("response", ""),
            "speech_rate": tts.get("rate", 150),
            "prosody_markers": tts.get("prosody", []),
            "emphasis_points": tts.get("emphasis", []),
            "tts_ready": tts.get("ready", False),
            "tts_confidence": tts.get("confidence", 0.0),
        })

        return state

    return process


def make_voice_interface_summary_node(llm: LLMFn):
    """
    Create Phase 21d voice interface summary node.

    Generates voice interaction summary.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate voice interface summary."""
        summary_lines = [
            "=== Voice & Conversation Interface ===",
        ]

        # Speech Detection
        if state.get("speech_detected"):
            summary_lines.append(f"\n🎤 Voice Input Detected")
            summary_lines.append(f"  Transcribed: \"{state.get('transcribed_text', '')[:60]}...\"")
            summary_lines.append(f"  Confidence: {state.get('speech_confidence', 0):.0%}")
            summary_lines.append(f"  Tone: {state.get('speech_tone', 'neutral')}")

        # Conversation Flow
        flow = state.get("conversation_flow", [])
        if flow:
            summary_lines.extend([
                f"\n💬 Conversation Flow ({len(flow)} turns):",
            ])
            for turn in flow[:2]:
                summary_lines.append(f"  → {turn}")

        # Natural Pauses
        pauses = state.get("natural_pauses", [])
        if pauses:
            summary_lines.extend([
                f"\n⏸️  Natural Pauses ({len(pauses)}):",
            ])
            for pause in pauses[:2]:
                summary_lines.append(f"  • {pause}ms pause")

        # Spoken Response
        spoken = state.get("spoken_response", "")
        if spoken:
            summary_lines.extend([
                f"\n🔊 Spoken Response:",
                f"  {spoken[:80]}...",
                f"  Speech Rate: {state.get('speech_rate', 150)} words/min",
            ])

        # Emphasis Points
        emphasis = state.get("emphasis_points", [])
        if emphasis:
            summary_lines.extend([
                f"\n⭐ Emphasis Points ({len(emphasis)}):",
            ])
            for point in emphasis[:2]:
                summary_lines.append(f"  • {point}")

        # Ready Status
        summary_lines.extend([
            f"\n✨ Voice Interface Status:",
            f"  TTS Ready: {'✓ YES' if state.get('tts_ready') else '✗ NO'}",
            f"  TTS Confidence: {state.get('tts_confidence', 0):.0%}",
            f"  Conversation Confidence: {state.get('conversation_confidence', 0):.0%}",
        ])

        phase21_summary = "\n".join(summary_lines)

        state.update({
            "phase21_summary": phase21_summary,
            "voice_interface_ready": True,
        })

        return state

    return process


def _process_voice_input(llm: LLMFn, state: FullAgentState) -> dict:
    """Process voice input and transcribe."""
    prompt = f"""Process voice input and transcribe:

Current Context: {state.get('input_text', 'no voice input')[:50]}
Speaker Profile: {state.get('user_profile', {}).get('name', 'user')}

Provide:
SPEECH_DETECTED: [true/false]
TRANSCRIBED_TEXT: [what was said]
SPEECH_CONFIDENCE: [0.0-1.0 transcription accuracy]
SPEECH_TONE: [how it was said: calm/urgent/curious/frustrated/excited/etc]
VOICE_CHARACTERISTICS: [speaker traits: age, accent, mood indicators]"""

    response = llm(prompt)
    return _parse_voice_response(response)


def _parse_voice_response(response: str) -> dict:
    """Parse voice processing response."""
    voice = {
        "detected": False,
        "text": "",
        "confidence": 0.0,
        "tone": "neutral",
        "characteristics": {},
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("SPEECH_DETECTED:"):
            detected_str = line.split(":", 1)[-1].strip().lower()
            voice["detected"] = detected_str in ["true", "yes", "1"]

        elif line.startswith("TRANSCRIBED_TEXT:"):
            voice["text"] = line.split(":", 1)[-1].strip()

        elif line.startswith("SPEECH_CONFIDENCE:"):
            try:
                voice["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                voice["confidence"] = 0.0

        elif line.startswith("SPEECH_TONE:"):
            voice["tone"] = line.split(":", 1)[-1].strip().lower()

        elif line.startswith("VOICE_CHARACTERISTICS:"):
            chars_str = line.split(":", 1)[-1].strip()
            voice["characteristics"] = {"description": chars_str}

    return voice


def _generate_conversation_flow(llm: LLMFn, state: FullAgentState, text: str) -> dict:
    """Generate natural conversation flow."""
    prompt = f"""Manage natural conversation flow:

User Said: {text}
Previous Context: {state.get('conversation_context', {}) if state.get('conversation_context') else 'first message'}
Emotional State: {state.get('emotional_state', 'neutral')}

Provide:
CONVERSATION_FLOW: [conversation structure and turns]
NATURAL_PAUSES: [where to pause in milliseconds]
INTERRUPTION_POINTS: [where user might interrupt]
CONTEXT: [maintain conversation context]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_flow_response(response)


def _parse_flow_response(response: str) -> dict:
    """Parse conversation flow response."""
    flow = {
        "context": {},
        "flow": [],
        "pauses": [],
        "interruptions": [],
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CONVERSATION_FLOW:"):
            flow_str = line.split(":", 1)[-1].strip()
            if flow_str:
                turns = [t.strip().strip("[](),") for t in flow_str.split(",")]
                flow["flow"] = [t for t in turns if t]

        elif line.startswith("NATURAL_PAUSES:"):
            pauses_str = line.split(":", 1)[-1].strip()
            if pauses_str:
                pauses = [p.strip().strip("[](),ms") for p in pauses_str.split(",")]
                flow["pauses"] = [p for p in pauses if p]

        elif line.startswith("INTERRUPTION_POINTS:"):
            ints_str = line.split(":", 1)[-1].strip()
            if ints_str:
                interruptions = [i.strip().strip("[](),") for i in ints_str.split(",")]
                flow["interruptions"] = [i for i in interruptions if i]

        elif line.startswith("CONFIDENCE:"):
            try:
                flow["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                flow["confidence"] = 0.75

    return flow


def _generate_tts(llm: LLMFn, state: FullAgentState, text: str, tone: str) -> dict:
    """Generate text-to-speech with natural prosody."""
    prompt = f"""Generate natural speech from text:

Text: {text}
Tone: {tone}
Speaker Profile: {state.get('user_profile', {}).get('name', 'JARVIS')}
Emotional Support Level: {state.get('emotional_support_level', 0.5):.0%}

Provide:
SPEECH_RATE: [words per minute, 120-180 for natural]
PROSODY_MARKERS: [where to adjust pitch/volume]
EMPHASIS_POINTS: [words to emphasize]
READY: [true/false if can be spoken]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_tts_response(response, text)


def _parse_tts_response(response: str, text: str) -> dict:
    """Parse TTS generation response."""
    tts = {
        "response": text,
        "rate": 150,
        "prosody": [],
        "emphasis": [],
        "ready": False,
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("SPEECH_RATE:"):
            try:
                tts["rate"] = int(line.split(":", 1)[-1].strip())
            except ValueError:
                tts["rate"] = 150

        elif line.startswith("PROSODY_MARKERS:"):
            prosody_str = line.split(":", 1)[-1].strip()
            if prosody_str:
                prosody = [p.strip().strip("[](),") for p in prosody_str.split(",")]
                tts["prosody"] = [p for p in prosody if p]

        elif line.startswith("EMPHASIS_POINTS:"):
            emphasis_str = line.split(":", 1)[-1].strip()
            if emphasis_str:
                emphasis = [e.strip().strip("[](),") for e in emphasis_str.split(",")]
                tts["emphasis"] = [e for e in emphasis if e]

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            tts["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                tts["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                tts["confidence"] = 0.75

    return tts
