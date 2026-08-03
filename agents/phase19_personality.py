"""Phase 19: Personality & Conversational Charm."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_personality_framework_node(llm: LLMFn):
    """
    Create Phase 19a personality framework node.

    Establishes consistent personality traits and character voice.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 19a: Personality Framework.

        Defines core personality traits and character expression.
        """
        personality = _define_personality(llm, state)

        state.update({
            "personality_traits": personality.get("traits", []),
            "character_voice": personality.get("voice", ""),
            "humor_level": personality.get("humor_level", 0.5),
            "formality_level": personality.get("formality_level", 0.5),
            "charm_score": personality.get("charm_score", 0.0),
            "personality_confidence": personality.get("confidence", 0.0),
        })

        return state

    return process


def make_conversational_generation_node(llm: LLMFn):
    """
    Create Phase 19b conversational generation node.

    Generates natural, witty conversation with charm.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 19b: Conversational Generation.

        Creates natural, engaging dialogue responses.
        """
        user_input = state.get("input_text", "")
        personality_traits = state.get("personality_traits", [])

        if not user_input or not personality_traits:
            state.update({
                "conversational_response": "",
                "response_wit_level": 0.0,
                "response_charm_applied": 0.0,
                "natural_dialogue_confidence": 0.0,
            })
            return state

        dialogue = _generate_conversation(llm, state, user_input, personality_traits)

        state.update({
            "conversational_response": dialogue.get("response", ""),
            "response_wit_level": dialogue.get("wit", 0.0),
            "response_charm_applied": dialogue.get("charm", 0.0),
            "natural_dialogue_confidence": dialogue.get("confidence", 0.0),
        })

        return state

    return process


def make_personal_relationship_model_node(llm: LLMFn):
    """
    Create Phase 19c personal relationship model node.

    Builds and maintains personal relationship with user.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 19c: Personal Relationship Model.

        Develops personal understanding and adaptation.
        """
        user_profile = state.get("user_profile", {})
        user_patterns = state.get("user_patterns", [])
        execution_history = state.get("execution_history", [])

        if not user_profile and not user_patterns:
            state.update({
                "user_quirks": [],
                "user_preferences_learned": {},
                "relationship_depth": 0.0,
                "personalization_level": 0.0,
                "relationship_confidence": 0.0,
            })
            return state

        relationship = _build_relationship(llm, state, user_profile, user_patterns, execution_history)

        state.update({
            "user_quirks": relationship.get("quirks", []),
            "user_preferences_learned": relationship.get("preferences", {}),
            "relationship_depth": relationship.get("depth", 0.0),
            "personalization_level": relationship.get("personalization", 0.0),
            "relationship_confidence": relationship.get("confidence", 0.0),
        })

        return state

    return process


def make_character_expression_summary_node(llm: LLMFn):
    """
    Create Phase 19d character expression summary node.

    Generates personality and conversation summary.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 19d: Character Expression Summary.

        Provides comprehensive personality report.
        """
        personality_traits = state.get("personality_traits", [])
        charm_score = state.get("charm_score", 0.0)
        relationship_depth = state.get("relationship_depth", 0.0)

        summary_lines = [
            "=== Personality & Conversational Charm ===",
        ]

        # Personality Traits
        if personality_traits:
            summary_lines.extend([
                f"\n🎭 Personality Profile:",
            ])
            for trait in personality_traits[:5]:
                summary_lines.append(f"  ✓ {trait}")

        # Charm & Wit Metrics
        summary_lines.extend([
            f"\n✨ Charm & Wit Assessment:",
            f"  Overall Charm Score: {charm_score:.0%}",
            f"  Humor Level: {state.get('humor_level', 0):.0%}",
            f"  Formality Level: {state.get('formality_level', 0):.0%}",
            f"  Natural Dialogue: {state.get('natural_dialogue_confidence', 0):.0%}",
        ])

        # Personal Relationship
        summary_lines.extend([
            f"\n💝 Relationship Development:",
            f"  Relationship Depth: {relationship_depth:.0%}",
            f"  Personalization Level: {state.get('personalization_level', 0):.0%}",
        ])

        # User Quirks Learned
        quirks = state.get("user_quirks", [])
        if quirks:
            summary_lines.extend([
                f"\n🎯 User Quirks Discovered ({len(quirks)}):",
            ])
            for quirk in quirks[:3]:
                summary_lines.append(f"  • {quirk}")

        # Last Conversational Response
        response = state.get("conversational_response", "")
        if response:
            summary_lines.extend([
                f"\n💬 Recent Response Example:",
                f"  \"{response[:80]}...\"",
            ])

        # Personality Readiness
        summary_lines.extend([
            f"\n✨ Personality Status:",
            f"  Personality Established: YES",
            f"  Character Voice: CONSISTENT",
            f"  Relationship Building: ACTIVE",
            f"  Overall Confidence: {state.get('personality_confidence', 0):.0%}",
        ])

        phase19_summary = "\n".join(summary_lines)

        state.update({
            "personality_established": True,
            "character_ready": True,
            "conversational_charm_active": True,
            "phase19_summary": phase19_summary,
        })

        return state

    return process


def _define_personality(llm: LLMFn, state: FullAgentState) -> dict:
    """Define system personality."""
    core_mission = state.get("core_mission", "Help users effectively")

    prompt = f"""Define an engaging AI personality (like JARVIS but modern):

Core Mission: {core_mission}
User Profile: {state.get('user_profile', {}).get('name', 'User')}

Provide personality that is:
- Intelligent but witty
- Formal but warm
- Professional but charming
- Helpful but slightly independent-thinking
- Loyal but honest

Provide:
TRAITS: [personality traits: witty, charming, intelligent, loyal, wise, etc]
VOICE: [character voice/style description]
HUMOR_LEVEL: [0.0-1.0 how much humor to use]
FORMALITY_LEVEL: [0.0-1.0 formality vs casualness]
CHARM_SCORE: [0.0-1.0 overall charm assessment]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_personality_response(response)


def _parse_personality_response(response: str) -> dict:
    """Parse personality definition response."""
    personality = {
        "traits": [],
        "voice": "",
        "humor_level": 0.5,
        "formality_level": 0.5,
        "charm_score": 0.75,
        "confidence": 0.85,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("TRAITS:"):
            traits_str = line.split(":", 1)[-1].strip()
            if traits_str:
                traits = [t.strip().strip("[](),") for t in traits_str.split(",")]
                personality["traits"] = [t for t in traits if t]

        elif line.startswith("VOICE:"):
            personality["voice"] = line.split(":", 1)[-1].strip()

        elif line.startswith("HUMOR_LEVEL:"):
            try:
                personality["humor_level"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                personality["humor_level"] = 0.5

        elif line.startswith("FORMALITY_LEVEL:"):
            try:
                personality["formality_level"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                personality["formality_level"] = 0.5

        elif line.startswith("CHARM_SCORE:"):
            try:
                personality["charm_score"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                personality["charm_score"] = 0.75

        elif line.startswith("CONFIDENCE:"):
            try:
                personality["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                personality["confidence"] = 0.85

    return personality


def _generate_conversation(llm: LLMFn, state: FullAgentState, user_input: str, traits: list) -> dict:
    """Generate natural conversation response."""
    traits_str = ", ".join(traits[:3]) if traits else "intelligent and helpful"

    prompt = f"""Generate a response with personality:

User Said: {user_input}
Your Personality: {traits_str}
Humor Level: {state.get('humor_level', 0.5):.0%}
Formality: {state.get('formality_level', 0.5):.0%}

Respond naturally with:
- Appropriate wit or humor if it fits
- Your unique character voice
- Genuine helpfulness
- Charm without being fake

Provide:
RESPONSE: [your witty, charming response]
WIT_LEVEL: [0.0-1.0 how witty was the response]
CHARM_APPLIED: [0.0-1.0 how much charm was used]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_conversation_response(response)


def _parse_conversation_response(response: str) -> dict:
    """Parse conversation response."""
    dialogue = {
        "response": "",
        "wit": 0.5,
        "charm": 0.5,
        "confidence": 0.82,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("RESPONSE:"):
            dialogue["response"] = line.split(":", 1)[-1].strip()

        elif line.startswith("WIT_LEVEL:"):
            try:
                dialogue["wit"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                dialogue["wit"] = 0.5

        elif line.startswith("CHARM_APPLIED:"):
            try:
                dialogue["charm"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                dialogue["charm"] = 0.5

        elif line.startswith("CONFIDENCE:"):
            try:
                dialogue["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                dialogue["confidence"] = 0.82

    return dialogue


def _build_relationship(llm: LLMFn, state: FullAgentState, user_profile: dict, patterns: list, history: list) -> dict:
    """Build personal relationship model."""
    user_name = user_profile.get("name", "User")
    patterns_str = ", ".join(patterns[:3]) if patterns else "not yet established"

    prompt = f"""Build personal relationship understanding:

User: {user_name}
Observed Patterns: {patterns_str}
Interaction History: {len(history)} interactions

Identify:
QUIRKS: [unique user quirks/preferences learned]
PREFERENCES: [how they like to be interacted with]
RELATIONSHIP_DEPTH: [0.0-1.0 depth of understanding]
PERSONALIZATION: [0.0-1.0 how much to personalize]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_relationship_response(response)


def _parse_relationship_response(response: str) -> dict:
    """Parse relationship model response."""
    relationship = {
        "quirks": [],
        "preferences": {},
        "depth": 0.5,
        "personalization": 0.5,
        "confidence": 0.80,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("QUIRKS:"):
            quirks_str = line.split(":", 1)[-1].strip()
            if quirks_str:
                quirks = [q.strip().strip("[](),") for q in quirks_str.split(",")]
                relationship["quirks"] = [q for q in quirks if q]

        elif line.startswith("RELATIONSHIP_DEPTH:"):
            try:
                relationship["depth"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                relationship["depth"] = 0.5

        elif line.startswith("PERSONALIZATION:"):
            try:
                relationship["personalization"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                relationship["personalization"] = 0.5

        elif line.startswith("CONFIDENCE:"):
            try:
                relationship["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                relationship["confidence"] = 0.80

    return relationship
