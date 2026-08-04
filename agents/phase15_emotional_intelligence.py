"""Phase 15: Emotional Intelligence & Sentiment Analysis."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_sentiment_analysis_node(llm: LLMFn):
    """
    Create Phase 15a sentiment analysis node.

    Analyzes emotional tone and sentiment in user input.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 15a: Sentiment Analysis.

        Detects emotional tone and sentiment.
        """
        sentiment = _analyze_sentiment(llm, state)

        state.update({
            "user_sentiment": sentiment.get("sentiment", "neutral"),
            "sentiment_score": sentiment.get("score", 0.0),
            "emotional_tone": sentiment.get("tone", []),
            "sentiment_confidence": sentiment.get("confidence", 0.0),
        })

        return state

    return process


def make_emotion_detection_node(llm: LLMFn):
    """
    Create Phase 15b emotion detection node.

    Detects specific emotions in user communication.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 15b: Emotion Detection.

        Identifies specific emotions and emotional states.
        """
        user_input = state.get("input_text", "")
        sentiment = state.get("user_sentiment", "neutral")

        if not user_input:
            state.update({
                "detected_emotions": [],
                "emotion_intensities": {},
                "emotional_state": "neutral",
                "emotion_detection_confidence": 0.0,
            })
            return state

        emotions = _detect_emotions(llm, state, user_input, sentiment)

        state.update({
            "detected_emotions": emotions.get("emotions", []),
            "emotion_intensities": emotions.get("intensities", {}),
            "emotional_state": emotions.get("state", "neutral"),
            "emotion_detection_confidence": emotions.get("confidence", 0.0),
        })

        return state

    return process


def make_empathy_response_node(llm: LLMFn):
    """
    Create Phase 15c empathy response node.

    Generates emotionally appropriate responses.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 15c: Empathy Response.

        Creates responses that match emotional context.
        """
        emotions = state.get("detected_emotions", [])
        sentiment = state.get("user_sentiment", "neutral")

        if not emotions:
            state.update({
                "empathetic_response": "",
                "response_tone_adjustment": "neutral",
                "emotional_support_level": 0.0,
            })
            return state

        response = _generate_empathy_response(llm, state, emotions, sentiment)

        state.update({
            "empathetic_response": response.get("response", ""),
            "response_tone_adjustment": response.get("tone", "neutral"),
            "emotional_support_level": response.get("support_level", 0.0),
            "empathy_confidence": response.get("confidence", 0.0),
        })

        return state

    return process


def make_emotional_intelligence_summary_node(llm: LLMFn):
    """
    Create Phase 15d emotional intelligence summary node.

    Generates emotional intelligence report.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate emotional intelligence summary."""
        summary_lines = [
            "=== Emotional Intelligence Mode ===",
        ]

        # Sentiment
        sentiment = state.get("user_sentiment", "neutral")
        sentiment_score = state.get("sentiment_score", 0.0)
        summary_lines.append(f"\n💭 Sentiment: {sentiment} ({sentiment_score:+.0%})")

        # Emotional Tone
        tones = state.get("emotional_tone", [])
        if tones:
            summary_lines.extend([
                f"\n🎭 Emotional Tones ({len(tones)}):",
            ])
            for tone in tones[:3]:
                summary_lines.append(f"  • {tone}")

        # Detected Emotions
        emotions = state.get("detected_emotions", [])
        if emotions:
            summary_lines.extend([
                f"\n❤️  Detected Emotions ({len(emotions)}):",
            ])
            intensities = state.get("emotion_intensities", {})
            for emotion in emotions[:5]:
                intensity = intensities.get(emotion, 0)
                intensity_bar = "█" * int(intensity * 5)
                summary_lines.append(f"  {emotion}: {intensity_bar} {intensity:.0%}")

        # Emotional State
        emotional_state = state.get("emotional_state", "neutral")
        summary_lines.append(f"\n🧠 Overall Emotional State: {emotional_state}")

        # Empathetic Response
        empathy = state.get("empathetic_response", "")
        if empathy:
            summary_lines.extend([
                f"\n💬 Empathetic Response:",
                f"  {empathy[:80]}..." if len(empathy) > 80 else f"  {empathy}",
            ])

        # Support Level
        support = state.get("emotional_support_level", 0.0)
        summary_lines.append(f"\n🤝 Emotional Support Level: {support:.0%}")

        # Confidence Metrics
        summary_lines.extend([
            f"\n✨ Emotional Intelligence Metrics:",
            f"  Sentiment: {state.get('sentiment_confidence', 0):.0%}",
            f"  Emotion Detection: {state.get('emotion_detection_confidence', 0):.0%}",
            f"  Empathy: {state.get('empathy_confidence', 0):.0%}",
        ])

        phase15_summary = "\n".join(summary_lines)

        state.update({
            "phase15_summary": phase15_summary,
            "emotional_intelligence_ready": True,
        })

        return state

    return process


def _analyze_sentiment(llm: LLMFn, state: FullAgentState) -> dict:
    """Analyze sentiment of user input."""
    user_input = state.get("input_text", "")

    prompt = f"""Analyze sentiment and emotional tone:

User Input: {user_input}
Context: {state.get('user_status', 'neutral')}

Provide:
SENTIMENT: [positive/negative/neutral]
SENTIMENT_SCORE: [-1.0 to 1.0, where -1 is very negative, 0 is neutral, 1 is very positive]
EMOTIONAL_TONE: [list of emotional tones detected]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_sentiment_response(response)


def _parse_sentiment_response(response: str) -> dict:
    """Parse sentiment analysis response."""
    sentiment = {
        "sentiment": "neutral",
        "score": 0.0,
        "tone": [],
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("SENTIMENT:"):
            sentiment["sentiment"] = line.split(":", 1)[-1].strip().lower()

        elif line.startswith("SENTIMENT_SCORE:"):
            try:
                sentiment["score"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                sentiment["score"] = 0.0

        elif line.startswith("EMOTIONAL_TONE:"):
            tones_str = line.split(":", 1)[-1].strip()
            if tones_str:
                tones = [t.strip().strip("[](),") for t in tones_str.split(",")]
                sentiment["tone"] = [t for t in tones if t]

        elif line.startswith("CONFIDENCE:"):
            try:
                sentiment["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                sentiment["confidence"] = 0.75

    return sentiment


def _detect_emotions(llm: LLMFn, state: FullAgentState, user_input: str, sentiment: str) -> dict:
    """Detect specific emotions."""
    prompt = f"""Detect specific emotions in user communication:

User Input: {user_input}
Overall Sentiment: {sentiment}
User Context: {state.get('user_profile', {}).get('personality', 'unknown')}

Provide:
EMOTIONS: [specific emotions detected: joy, sadness, anger, fear, surprise, disgust, trust, anticipation]
EMOTION_INTENSITIES: [0.0-1.0 intensity for each emotion]
EMOTIONAL_STATE: [current emotional state]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_emotion_response(response)


def _parse_emotion_response(response: str) -> dict:
    """Parse emotion detection response."""
    emotions = {
        "emotions": [],
        "intensities": {},
        "state": "neutral",
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("EMOTIONS:"):
            emotions_str = line.split(":", 1)[-1].strip()
            if emotions_str:
                emotion_list = [e.strip().strip("[](),") for e in emotions_str.split(",")]
                emotions["emotions"] = [e for e in emotion_list if e]

        elif line.startswith("EMOTION_INTENSITIES:"):
            intensities_str = line.split(":", 1)[-1].strip()
            if intensities_str:
                try:
                    pairs = [p.strip() for p in intensities_str.split(",")]
                    for pair in pairs:
                        if ":" in pair:
                            emotion, intensity = pair.split(":", 1)
                            emotions["intensities"][emotion.strip()] = float(intensity.strip())
                except (ValueError, IndexError):
                    pass

        elif line.startswith("EMOTIONAL_STATE:"):
            emotions["state"] = line.split(":", 1)[-1].strip().lower()

        elif line.startswith("CONFIDENCE:"):
            try:
                emotions["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                emotions["confidence"] = 0.75

    return emotions


def _generate_empathy_response(llm: LLMFn, state: FullAgentState, emotions: list, sentiment: str) -> dict:
    """Generate empathetic response."""
    emotions_str = ", ".join(emotions[:3])

    prompt = f"""Generate emotionally intelligent response:

Detected Emotions: {emotions_str}
Sentiment: {sentiment}
User Needs: {state.get('predicted_needs', [])[0] if state.get('predicted_needs') else 'support'}

Provide:
EMPATHETIC_RESPONSE: [response that acknowledges and validates emotions]
RESPONSE_TONE: [adjust_tone: warm/supportive/encouraging/calm/energetic]
EMOTIONAL_SUPPORT_LEVEL: [0.0-1.0 how much support is offered]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_empathy_response(response)


def _parse_empathy_response(response: str) -> dict:
    """Parse empathy response."""
    empathy = {
        "response": "",
        "tone": "neutral",
        "support_level": 0.5,
        "confidence": 0.75,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("EMPATHETIC_RESPONSE:"):
            empathy["response"] = line.split(":", 1)[-1].strip()

        elif line.startswith("RESPONSE_TONE:"):
            tone_str = line.split(":", 1)[-1].strip().lower()
            empathy["tone"] = tone_str

        elif line.startswith("EMOTIONAL_SUPPORT_LEVEL:"):
            try:
                empathy["support_level"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                empathy["support_level"] = 0.5

        elif line.startswith("CONFIDENCE:"):
            try:
                empathy["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                empathy["confidence"] = 0.75

    return empathy
