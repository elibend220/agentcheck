"""Phase 6: Learning & Feedback Loop Analysis."""

from __future__ import annotations

from typing import Callable, Any
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_learning_feedback_node(llm: LLMFn):
    """
    Create Phase 6 learning and feedback loop node.

    Analyzes execution results, extracts lessons, and generates recommendations
    for improving future tool selections and reasoning.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 6: Learning & Feedback Loop.

        Analyzes what worked, what didn't, and generates insights for improvement.
        """
        # Evaluate overall execution outcome
        outcome, confidence = _evaluate_outcome(state)

        # Extract lessons from execution
        lessons = _extract_lessons(llm, state, outcome)

        # Score tool performance
        tool_scores = _score_tool_performance(state)

        # Score phase performance
        phase_scores = _score_phase_performance(state)

        # Identify effective combinations
        combinations = _identify_effective_combinations(state)

        # Analyze failures if present
        failure_analysis = _analyze_failures(llm, state, outcome) if outcome == "failure" else {}

        # Generate improvement suggestions
        suggestions = _generate_suggestions(llm, state, lessons, tool_scores, phase_scores)

        # Compute learning metrics
        metrics = _compute_learning_metrics(
            state, outcome, tool_scores, phase_scores, lessons
        )

        # Update state
        state.update({
            "execution_outcome": outcome,
            "outcome_confidence": confidence,
            "lessons_learned": lessons,
            "tool_performance_scores": tool_scores,
            "phase_performance_scores": phase_scores,
            "improvement_suggestions": suggestions,
            "effective_tool_combinations": combinations,
            "failure_analysis": failure_analysis,
            "learning_metrics": metrics,
        })

        return state

    return process


def _evaluate_outcome(state: FullAgentState) -> tuple[str, float]:
    """Evaluate whether execution was successful."""
    execution_results = state.get("tool_execution_results", [])
    verification_results = state.get("verification_results", [])

    if not execution_results:
        return "success", 1.0

    success_count = sum(1 for r in execution_results if r.success)
    total_count = len(execution_results)
    success_rate = success_count / total_count if total_count > 0 else 0.0

    verification_valid = sum(1 for r in verification_results if r.valid)
    verification_total = len(verification_results)
    valid_rate = verification_valid / verification_total if verification_total > 0 else 1.0

    overall_success = (success_rate + valid_rate) / 2

    if overall_success >= 0.8:
        outcome = "success"
        confidence = overall_success
    elif overall_success >= 0.5:
        outcome = "partial"
        confidence = overall_success
    else:
        outcome = "failure"
        confidence = 1.0 - overall_success

    return outcome, confidence


def _extract_lessons(llm: LLMFn, state: FullAgentState, outcome: str) -> list[str]:
    """Extract key lessons from execution."""
    prompt = f"""Based on this execution analysis, extract 3-5 key lessons learned:

Input: {state.get('input_text', 'N/A')}
Execution Outcome: {outcome}
Selected Tools: {', '.join(state.get('selected_tools', []))}
Tool Execution Results: {len(state.get('tool_execution_results', []))} tools executed
Verification Results: {len(state.get('verification_results', []))} verification checks
Reasoning Type: {state.get('reasoning_type', 'N/A')}

Format your response as:
LESSON 1: [lesson]
LESSON 2: [lesson]
LESSON 3: [lesson]
etc."""

    response = llm(prompt)
    lessons = _parse_lessons(response)
    return lessons


def _parse_lessons(response: str) -> list[str]:
    """Parse lessons from LLM response."""
    lessons = []
    lines = response.split("\n")
    for line in lines:
        if line.startswith("LESSON"):
            lesson = line.split(":", 1)[-1].strip()
            if lesson:
                lessons.append(lesson)
    return lessons if lessons else ["Execution completed with useful insights"]


def _score_tool_performance(state: FullAgentState) -> dict[str, float]:
    """Score performance of each executed tool."""
    scores = {}
    execution_results = state.get("tool_execution_results", [])

    for result in execution_results:
        tool_id = result.tool_id
        # Score based on success, execution time, and confidence
        base_score = 1.0 if result.success else 0.0
        time_penalty = min(result.execution_time_ms / 5000.0, 0.2)  # Max 0.2 penalty for slowness
        confidence_factor = result.confidence
        final_score = (base_score - time_penalty) * confidence_factor
        scores[tool_id] = max(0.0, min(1.0, final_score))

    return scores


def _score_phase_performance(state: FullAgentState) -> dict[str, float]:
    """Score performance of each phase."""
    scores = {}

    # Phase 1: NLP
    nlp_has_intent = bool(state.get("intent"))
    nlp_has_entities = bool(state.get("entities"))
    scores["phase1_nlp"] = 1.0 if (nlp_has_intent and nlp_has_entities) else 0.5

    # Phase 2: Knowledge
    has_knowledge = bool(state.get("relevant_knowledge"))
    scores["phase2_knowledge"] = 1.0 if has_knowledge else 0.5

    # Phase 3a: Consciousness
    has_attention = bool(state.get("attention_focus"))
    has_metacognition = bool(state.get("metacognitive_notes"))
    scores["phase3a_consciousness"] = 1.0 if (has_attention and has_metacognition) else 0.5

    # Phase 3b: Reasoning
    has_reasoning = bool(state.get("reasoning_type"))
    has_conclusion = bool(state.get("reasoning_conclusion"))
    scores["phase3b_reasoning"] = 1.0 if (has_reasoning and has_conclusion) else 0.5

    # Phase 3c: Creativity
    has_ideas = bool(state.get("creative_ideas"))
    scores["phase3c_creativity"] = 1.0 if has_ideas else 0.5

    # Phase 4: Tool Execution
    execution_results = state.get("tool_execution_results", [])
    if execution_results:
        success_rate = sum(1 for r in execution_results if r.success) / len(execution_results)
        scores["phase4_tools"] = success_rate
    else:
        scores["phase4_tools"] = 0.5

    # Phase 5: Quantum
    quantum_created = state.get("quantum_state_created", False)
    scores["phase5_quantum"] = 1.0 if quantum_created else 0.5

    return scores


def _identify_effective_combinations(state: FullAgentState) -> list[list[str]]:
    """Identify which tool combinations worked well."""
    execution_results = state.get("tool_execution_results", [])
    successful_tools = [r.tool_id for r in execution_results if r.success]

    if not successful_tools:
        return []

    # Check if verification confirmed success
    verification_results = state.get("verification_results", [])
    verified_tools = [r.tool_id for r in verification_results if r.valid]

    combinations = []
    if verified_tools:
        combinations.append(verified_tools)

    if len(successful_tools) > 1:
        combinations.append(successful_tools)

    return combinations


def _analyze_failures(llm: LLMFn, state: FullAgentState, outcome: str) -> dict[str, Any]:
    """Analyze why execution failed."""
    execution_results = state.get("tool_execution_results", [])
    failed_tools = [r for r in execution_results if not r.success]

    if not failed_tools:
        return {}

    prompt = f"""Analyze why these tools failed during execution:

Failed Tools:
{chr(10).join(f"  - {r.tool_id}: {r.error}" for r in failed_tools)}

Selected Tools: {', '.join(state.get('selected_tools', []))}
Input: {state.get('input_text', 'N/A')}
Reasoning: {state.get('reasoning_type', 'N/A')}

Provide analysis in this format:
ROOT_CAUSES: [list causes]
CONTRIBUTING_FACTORS: [list factors]
PREVENTION: [how to prevent]"""

    response = llm(prompt)

    return {
        "failed_tool_count": len(failed_tools),
        "failed_tools": [r.tool_id for r in failed_tools],
        "analysis": response,
    }


def _generate_suggestions(
    llm: LLMFn,
    state: FullAgentState,
    lessons: list[str],
    tool_scores: dict[str, float],
    phase_scores: dict[str, float],
) -> list[str]:
    """Generate suggestions for improvement."""
    # Identify weak phases
    weak_phases = [p for p, score in phase_scores.items() if score < 0.7]
    low_scoring_tools = [t for t, score in tool_scores.items() if score < 0.5]

    prompt = f"""Based on this execution analysis, provide 3-5 actionable improvement suggestions:

Weak Phases: {', '.join(weak_phases) if weak_phases else 'None'}
Low-Performing Tools: {', '.join(low_scoring_tools) if low_scoring_tools else 'None'}
Lessons Learned: {'; '.join(lessons[:3])}
Selected Tools: {', '.join(state.get('selected_tools', []))}

Format as:
SUGGESTION 1: [specific actionable suggestion]
SUGGESTION 2: [specific actionable suggestion]
etc."""

    response = llm(prompt)
    suggestions = _parse_suggestions(response)
    return suggestions


def _parse_suggestions(response: str) -> list[str]:
    """Parse suggestions from LLM response."""
    suggestions = []
    lines = response.split("\n")
    for line in lines:
        if line.startswith("SUGGESTION"):
            suggestion = line.split(":", 1)[-1].strip()
            if suggestion:
                suggestions.append(suggestion)
    return suggestions if suggestions else ["Increase tool diversity for future attempts"]


def _compute_learning_metrics(
    state: FullAgentState,
    outcome: str,
    tool_scores: dict[str, float],
    phase_scores: dict[str, float],
    lessons: list[str],
) -> dict[str, float]:
    """Compute quantitative learning metrics."""
    metrics = {}

    # Outcome score
    outcome_score = {"success": 1.0, "partial": 0.5, "failure": 0.0}
    metrics["outcome_score"] = outcome_score.get(outcome, 0.5)

    # Tool performance
    if tool_scores:
        metrics["avg_tool_performance"] = sum(tool_scores.values()) / len(tool_scores)
        metrics["best_tool_performance"] = max(tool_scores.values())
        metrics["worst_tool_performance"] = min(tool_scores.values())
    else:
        metrics["avg_tool_performance"] = 0.0
        metrics["best_tool_performance"] = 0.0
        metrics["worst_tool_performance"] = 0.0

    # Phase performance
    if phase_scores:
        metrics["avg_phase_performance"] = sum(phase_scores.values()) / len(phase_scores)
        metrics["best_phase_performance"] = max(phase_scores.values())
        metrics["worst_phase_performance"] = min(phase_scores.values())
    else:
        metrics["avg_phase_performance"] = 0.0
        metrics["best_phase_performance"] = 0.0
        metrics["worst_phase_performance"] = 0.0

    # Learning quality
    metrics["lessons_extracted"] = float(len(lessons))
    metrics["learning_quality"] = min(1.0, len(lessons) / 5.0)  # Higher for more lessons

    # Overall learning score
    metrics["overall_learning_score"] = (
        metrics["outcome_score"] * 0.4 +
        metrics["avg_tool_performance"] * 0.3 +
        metrics["avg_phase_performance"] * 0.3
    )

    return metrics


def make_phase6_summary_node(llm: LLMFn):
    """
    Create Phase 6 summary node.

    Generates human-readable summary of learning insights.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate summary of Phase 6 learning results."""
        outcome = state.get("execution_outcome", "unknown")
        lessons = state.get("lessons_learned", [])
        suggestions = state.get("improvement_suggestions", [])
        metrics = state.get("learning_metrics", {})

        summary_lines = [
            "=== Phase 6: Learning & Feedback Loop ===",
            f"Execution Outcome: {outcome.upper()}",
            f"Outcome Confidence: {state.get('outcome_confidence', 0):.2f}",
            f"",
            f"Key Lessons Learned ({len(lessons)}):",
        ]

        for i, lesson in enumerate(lessons[:3], 1):
            summary_lines.append(f"  {i}. {lesson}")

        summary_lines.extend([
            f"",
            f"Improvement Suggestions ({len(suggestions)}):",
        ])

        for i, suggestion in enumerate(suggestions[:3], 1):
            summary_lines.append(f"  {i}. {suggestion}")

        summary_lines.extend([
            f"",
            f"Performance Metrics:",
            f"  Overall Learning Score: {metrics.get('overall_learning_score', 0):.4f}",
            f"  Avg Tool Performance: {metrics.get('avg_tool_performance', 0):.4f}",
            f"  Avg Phase Performance: {metrics.get('avg_phase_performance', 0):.4f}",
        ])

        phase6_summary = "\n".join(summary_lines)

        state.update({
            "phase6_summary": phase6_summary,
        })

        return state

    return process
