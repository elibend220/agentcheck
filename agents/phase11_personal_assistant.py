"""Phase 11: Proactive Personal Assistant - JARVIS-like autonomous assistance."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_user_profile_node(llm: LLMFn):
    """
    Create Phase 11a user profile & context node.

    Builds understanding of user preferences, patterns, and current status.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 11a: User Profile & Context Building.

        Develops deep understanding of user for personalized assistance.
        """
        user_input = state.get("input_text", "")

        # Build user context profile
        user_profile = _build_user_profile(llm, state, user_input)

        state.update({
            "user_profile": user_profile.get("profile", {}),
            "user_status": user_profile.get("current_status", ""),
            "user_preferences": user_profile.get("preferences", {}),
            "user_patterns": user_profile.get("patterns", []),
        })

        return state

    return process


def make_predictive_assistance_node(llm: LLMFn):
    """
    Create Phase 11b predictive assistance node.

    Anticipates user needs before explicitly requested.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 11b: Predictive Assistance.

        Generates proactive suggestions and anticipates needs.
        """
        user_profile = state.get("user_profile", {})
        user_status = state.get("user_status", "")

        if not user_profile:
            state.update({
                "predicted_needs": [],
                "proactive_suggestions": [],
                "anticipation_confidence": 0.0,
            })
            return state

        # Generate predictions
        predictions = _generate_predictions(llm, state, user_profile, user_status)

        state.update({
            "predicted_needs": predictions.get("needs", []),
            "proactive_suggestions": predictions.get("suggestions", []),
            "anticipation_confidence": predictions.get("confidence", 0.0),
            "priority_actions": predictions.get("priority_actions", []),
        })

        return state

    return process


def make_autonomous_action_node(llm: LLMFn):
    """
    Create Phase 11c autonomous action node.

    Recommends and executes actions autonomously based on user profile.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 11c: Autonomous Actions.

        Takes initiative in executing identified tasks.
        """
        predicted_needs = state.get("predicted_needs", [])
        priority_actions = state.get("priority_actions", [])

        if not predicted_needs and not priority_actions:
            state.update({
                "autonomous_actions": [],
                "actions_recommended": False,
            })
            return state

        # Generate autonomous actions
        actions = _generate_autonomous_actions(llm, state, predicted_needs, priority_actions)

        state.update({
            "autonomous_actions": actions.get("actions", []),
            "actions_recommended": len(actions.get("actions", [])) > 0,
            "action_priorities": actions.get("priorities", []),
            "action_risks": actions.get("risks", []),
            "requires_confirmation": actions.get("requires_confirmation", False),
        })

        return state

    return process


def make_personal_assistant_summary_node(llm: LLMFn):
    """
    Create Phase 11d personal assistant summary node.

    Generates natural, conversational assistant response.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate personal assistant response."""
        summary_lines = [
            "=== Personal Assistant Mode ===",
        ]

        # User Status
        user_status = state.get("user_status", "")
        if user_status:
            summary_lines.append(f"\n📊 Status: {user_status}")

        # User Profile Insights
        profile = state.get("user_profile", {})
        if profile.get("name"):
            summary_lines.append(f"\n👤 User: {profile.get('name')}")

        if profile.get("current_activity"):
            summary_lines.append(f"📍 Currently: {profile.get('current_activity')}")

        # Predicted Needs
        needs = state.get("predicted_needs", [])
        if needs:
            summary_lines.extend([
                f"\n🔮 Anticipated Needs ({len(needs)}):",
            ])
            for need in needs[:3]:
                summary_lines.append(f"  • {need}")

        # Proactive Suggestions
        suggestions = state.get("proactive_suggestions", [])
        if suggestions:
            summary_lines.extend([
                f"\n💡 Suggestions ({len(suggestions)}):",
            ])
            for suggestion in suggestions[:3]:
                summary_lines.append(f"  • {suggestion}")

        # Priority Actions
        actions = state.get("priority_actions", [])
        if actions:
            summary_lines.extend([
                f"\n⚡ Priority Actions ({len(actions)}):",
            ])
            for action in actions[:3]:
                summary_lines.append(f"  → {action}")

        # Autonomous Recommendations
        auto_actions = state.get("autonomous_actions", [])
        if auto_actions:
            summary_lines.extend([
                f"\n🤖 Ready to Execute ({len(auto_actions)}):",
            ])
            for action in auto_actions[:3]:
                summary_lines.append(f"  ✓ {action}")

            if state.get("requires_confirmation"):
                summary_lines.append("\n  (Awaiting your confirmation to proceed)")

        # Confidence
        confidence = state.get("anticipation_confidence", 0)
        summary_lines.extend([
            f"\n✨ Confidence: {confidence:.0%}",
        ])

        phase11_summary = "\n".join(summary_lines)

        state.update({
            "phase11_summary": phase11_summary,
            "assistant_ready": True,
        })

        return state

    return process


def _build_user_profile(llm: LLMFn, state: FullAgentState, user_input: str) -> dict:
    """Build comprehensive user profile and context."""
    prompt = f"""Analyze this user interaction and build a user profile:

User Input: {user_input}
Previous Context: {state.get('summary', 'First interaction')}
Learning History: {len(state.get('lessons_learned', []))} previous interactions

Provide:
NAME: [user name if identifiable]
CURRENT_STATUS: [busy, available, focused, tired, etc.]
PREFERENCES: [list of known preferences]
PATTERNS: [behavioral patterns observed]
PERSONALITY: [communication style]
CURRENT_ACTIVITY: [what they're likely doing]
TONE_SUGGESTION: [how to communicate back]"""

    response = llm(prompt)
    return _parse_user_profile(response)


def _parse_user_profile(response: str) -> dict:
    """Parse user profile from LLM response."""
    profile_data = {
        "profile": {},
        "current_status": "",
        "preferences": {},
        "patterns": [],
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("NAME:"):
            profile_data["profile"]["name"] = line.split(":", 1)[-1].strip()
        elif line.startswith("CURRENT_STATUS:"):
            profile_data["current_status"] = line.split(":", 1)[-1].strip()
        elif line.startswith("PREFERENCES:"):
            prefs_str = line.split(":", 1)[-1].strip()
            if prefs_str:
                profile_data["preferences"]["stated"] = prefs_str
        elif line.startswith("PATTERNS:"):
            patterns_str = line.split(":", 1)[-1].strip()
            if patterns_str:
                profile_data["patterns"].append(patterns_str)
        elif line.startswith("PERSONALITY:"):
            profile_data["profile"]["personality"] = line.split(":", 1)[-1].strip()
        elif line.startswith("CURRENT_ACTIVITY:"):
            profile_data["profile"]["current_activity"] = line.split(":", 1)[-1].strip()
        elif line.startswith("TONE_SUGGESTION:"):
            profile_data["profile"]["tone"] = line.split(":", 1)[-1].strip()

    return profile_data


def _generate_predictions(
    llm: LLMFn, state: FullAgentState, user_profile: dict, user_status: str
) -> dict:
    """Generate predictive assistance based on user profile."""
    profile_summary = f"Status: {user_status}, Personality: {user_profile.get('personality', 'professional')}"

    prompt = f"""Based on user profile and context, predict their needs:

User Profile: {profile_summary}
Recent Intent: {state.get('intent', 'General assistance')}
Available Tools: {', '.join(state.get('selected_tools', []))}

Predict:
PREDICTED_NEEDS: [need1, need2, need3]
PROACTIVE_SUGGESTIONS: [suggestion1, suggestion2, suggestion3]
PRIORITY_ACTIONS: [action1, action2, action3]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_predictions(response)


def _parse_predictions(response: str) -> dict:
    """Parse predictions from LLM response."""
    predictions = {
        "needs": [],
        "suggestions": [],
        "priority_actions": [],
        "confidence": 0.5,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("PREDICTED_NEEDS:"):
            needs_str = line.split(":", 1)[-1].strip()
            if needs_str:
                predictions["needs"].append(needs_str)
        elif line.startswith("PROACTIVE_SUGGESTIONS:"):
            sug_str = line.split(":", 1)[-1].strip()
            if sug_str:
                predictions["suggestions"].append(sug_str)
        elif line.startswith("PRIORITY_ACTIONS:"):
            act_str = line.split(":", 1)[-1].strip()
            if act_str:
                predictions["priority_actions"].append(act_str)
        elif line.startswith("CONFIDENCE:"):
            try:
                predictions["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                predictions["confidence"] = 0.5
        elif line.strip() and line.startswith("  "):
            item = line.strip().lstrip("- ")
            if "need" in response.split(line)[0].lower():
                predictions["needs"].append(item)

    return predictions


def _generate_autonomous_actions(
    llm: LLMFn, state: FullAgentState, needs: list, priority_actions: list
) -> dict:
    """Generate autonomous action recommendations."""
    needs_str = "\n".join([f"  • {n}" for n in needs[:3]])
    actions_str = "\n".join([f"  • {a}" for a in priority_actions[:3]])

    prompt = f"""Recommend autonomous actions based on predicted needs:

Predicted Needs:
{needs_str}

Priority Actions:
{actions_str}

Current Confidence: {state.get('anticipation_confidence', 0):.0%}

Provide:
RECOMMENDED_ACTIONS: [action1, action2, action3]
ACTION_PRIORITIES: [high, medium, low]
RISKS: [risk1, risk2]
REQUIRES_CONFIRMATION: [true/false]"""

    response = llm(prompt)
    return _parse_autonomous_actions(response)


def _parse_autonomous_actions(response: str) -> dict:
    """Parse autonomous actions from LLM response."""
    actions_data = {
        "actions": [],
        "priorities": [],
        "risks": [],
        "requires_confirmation": False,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("RECOMMENDED_ACTIONS:"):
            act_str = line.split(":", 1)[-1].strip()
            if act_str:
                actions_data["actions"].append(act_str)
        elif line.startswith("ACTION_PRIORITIES:"):
            pri_str = line.split(":", 1)[-1].strip()
            if pri_str:
                actions_data["priorities"].append(pri_str)
        elif line.startswith("RISKS:"):
            risk_str = line.split(":", 1)[-1].strip()
            if risk_str:
                actions_data["risks"].append(risk_str)
        elif line.startswith("REQUIRES_CONFIRMATION:"):
            conf_str = line.split(":", 1)[-1].strip().lower()
            actions_data["requires_confirmation"] = conf_str in ["true", "yes"]
        elif line.strip() and line.startswith("  "):
            item = line.strip().lstrip("- ")
            if "action" in response.split(line)[0].lower():
                actions_data["actions"].append(item)

    return actions_data
