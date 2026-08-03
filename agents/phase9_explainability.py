"""Phase 9: Explainability & Interpretability - Decision Transparency & Auditability."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_reasoning_trace_node(llm: LLMFn):
    """
    Create Phase 9a reasoning trace node.

    Generates detailed reasoning traces explaining each phase's decisions.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 9a: Reasoning Trace Generation.

        Creates transparent explanation of how each phase arrived at its conclusions.
        """
        reasoning_traces = {}

        # Phase 1: NLP reasoning
        if state.get("intent"):
            phase1_trace = _generate_phase_trace(
                llm,
                "Phase 1: NLP Processing",
                state.get("input_text", ""),
                state.get("intent", ""),
                state.get("entities", {}),
                state.get("summary", ""),
            )
            reasoning_traces["phase1_nlp"] = phase1_trace

        # Phase 2: Knowledge reasoning
        if state.get("relevant_knowledge"):
            phase2_trace = _generate_phase_trace(
                llm,
                "Phase 2: Knowledge Retrieval",
                state.get("intent", ""),
                state.get("relevant_knowledge", []),
                state.get("knowledge_summary", ""),
                state.get("attention_focus", []),
            )
            reasoning_traces["phase2_knowledge"] = phase2_trace

        # Phase 3: Consciousness & Reasoning reasoning
        if state.get("attention_focus"):
            phase3a_trace = _generate_phase_trace(
                llm,
                "Phase 3a: Consciousness",
                state.get("attention_focus", []),
                state.get("metacognitive_notes", ""),
                state.get("intent", ""),
            )
            reasoning_traces["phase3a_consciousness"] = phase3a_trace

        if state.get("reasoning_conclusion"):
            phase3b_trace = _generate_phase_trace(
                llm,
                "Phase 3b: Reasoning",
                state.get("reasoning_type", ""),
                state.get("reasoning_steps", []),
                state.get("reasoning_conclusion", ""),
            )
            reasoning_traces["phase3b_reasoning"] = phase3b_trace

        if state.get("creative_ideas"):
            phase3c_trace = _generate_phase_trace(
                llm,
                "Phase 3c: Creativity",
                state.get("creative_ideas", []),
                state.get("analogies", []),
                state.get("novel_combinations", []),
            )
            reasoning_traces["phase3c_creativity"] = phase3c_trace

        # Phase 4: Tool Selection reasoning
        if state.get("selected_tools"):
            phase4_trace = _generate_phase_trace(
                llm,
                "Phase 4: Tool Selection & Execution",
                state.get("selected_tools", []),
                state.get("tool_selection_reasoning", ""),
                state.get("tool_selection_confidence", 0.0),
            )
            reasoning_traces["phase4_tools"] = phase4_trace

        # Phase 5: Quantum reasoning
        if state.get("quantum_state_created"):
            phase5_trace = _generate_phase_trace(
                llm,
                "Phase 5: Quantum Optimization",
                state.get("quantum_amplitudes", {}),
                state.get("quantum_optimized_tools", []),
                state.get("quantum_metrics", {}),
            )
            reasoning_traces["phase5_quantum"] = phase5_trace

        # Phase 6: Learning reasoning
        if state.get("execution_outcome"):
            phase6_trace = _generate_phase_trace(
                llm,
                "Phase 6: Learning & Feedback",
                state.get("execution_outcome", ""),
                state.get("lessons_learned", []),
                state.get("improvement_suggestions", []),
            )
            reasoning_traces["phase6_learning"] = phase6_trace

        # Phase 7: Memory reasoning
        if state.get("memory_persisted"):
            phase7_trace = _generate_phase_trace(
                llm,
                "Phase 7: Memory & Knowledge Integration",
                state.get("historical_lessons", []),
                state.get("phase7_recommended_approach", ""),
                state.get("similar_past_executions", 0),
            )
            reasoning_traces["phase7_memory"] = phase7_trace

        # Phase 8: Error Recovery reasoning
        if state.get("recovery_needed"):
            phase8_trace = _generate_phase_trace(
                llm,
                "Phase 8: Error Recovery & Intelligent Retry",
                state.get("recovery_strategy", ""),
                state.get("error_details", {}),
                state.get("retry_success", False),
            )
            reasoning_traces["phase8_recovery"] = phase8_trace

        state.update({
            "reasoning_traces": reasoning_traces,
        })

        return state

    return process


def make_confidence_justification_node(llm: LLMFn):
    """
    Create Phase 9b confidence justification node.

    Builds justification chains explaining confidence scores.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 9b: Confidence Justification.

        Generates explanations for confidence levels across all phases.
        """
        confidence_justifications = {}

        # Collect all confidence metrics
        confidences = {
            "tool_selection": state.get("tool_selection_confidence", 0.0),
            "outcome": state.get("outcome_confidence", 0.0),
            "phase7_synthesis": state.get("phase7_confidence", 0.0),
            "recovery": state.get("recovery_confidence", 0.0),
        }

        # Generate justification for each confidence score
        for phase_key, confidence_value in confidences.items():
            if confidence_value > 0:
                justification = _generate_confidence_justification(
                    llm, phase_key, confidence_value, state
                )
                confidence_justifications[phase_key] = justification

        state.update({
            "confidence_justifications": confidence_justifications,
            "overall_system_confidence": _calculate_overall_confidence(confidences),
        })

        return state

    return process


def make_decision_audit_log_node(llm: LLMFn):
    """
    Create Phase 9c decision audit log node.

    Maintains comprehensive audit trail of all decisions.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 9c: Decision Audit Log.

        Creates auditable record of all decisions and their justifications.
        """
        audit_entries = []

        # Decision 1: Intent Recognition
        if state.get("intent"):
            audit_entries.append({
                "timestamp": "phase1",
                "decision_type": "intent_recognition",
                "decision": state.get("intent"),
                "confidence": 0.85,
                "justification": "NLP analysis of input text",
                "entities_involved": list(state.get("entities", {}).keys()),
                "reversible": True,
            })

        # Decision 2: Tool Selection
        if state.get("selected_tools"):
            audit_entries.append({
                "timestamp": "phase4",
                "decision_type": "tool_selection",
                "decision": state.get("selected_tools", []),
                "confidence": state.get("tool_selection_confidence", 0.0),
                "justification": state.get("tool_selection_reasoning", ""),
                "alternatives_considered": _extract_alternatives(state),
                "reversible": True,
            })

        # Decision 3: Execution Strategy
        if state.get("execution_outcome"):
            audit_entries.append({
                "timestamp": "phase6",
                "decision_type": "execution_outcome",
                "decision": state.get("execution_outcome"),
                "confidence": state.get("outcome_confidence", 0.0),
                "justification": f"Execution completed with {state.get('execution_outcome')} status",
                "failure_analysis": state.get("failure_analysis", {}),
                "reversible": False,
            })

        # Decision 4: Recovery Strategy (if applicable)
        if state.get("recovery_needed"):
            audit_entries.append({
                "timestamp": "phase8",
                "decision_type": "recovery_strategy",
                "decision": state.get("recovery_strategy", ""),
                "confidence": state.get("recovery_confidence", 0.0),
                "justification": f"Using {state.get('recovery_strategy')} for error recovery",
                "root_cause": state.get("error_details", {}).get("root_cause", "unknown"),
                "reversible": True,
            })

        state.update({
            "decision_audit_log": audit_entries,
            "audit_log_size": len(audit_entries),
        })

        return state

    return process


def make_explainability_summary_node(llm: LLMFn):
    """
    Create Phase 9d explainability summary node.

    Generates comprehensive summary of all explanations.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate comprehensive explainability summary."""
        summary_lines = [
            "=== Phase 9: Explainability & Interpretability ===",
        ]

        # Section 1: Reasoning Traces
        reasoning_traces = state.get("reasoning_traces", {})
        if reasoning_traces:
            summary_lines.extend([
                "\n## Reasoning Traces",
                f"Total phases traced: {len(reasoning_traces)}",
            ])
            for phase_name in sorted(reasoning_traces.keys()):
                trace = reasoning_traces[phase_name]
                summary_lines.append(
                    f"  ✓ {phase_name}: {trace.get('summary', 'N/A')[:60]}..."
                )

        # Section 2: Confidence Justifications
        confidence_just = state.get("confidence_justifications", {})
        if confidence_just:
            summary_lines.extend([
                "\n## Confidence Analysis",
                f"Overall System Confidence: {state.get('overall_system_confidence', 0):.2%}",
            ])
            for phase_key, justification in sorted(confidence_just.items()):
                summary_lines.append(
                    f"  • {phase_key}: {justification.get('reasoning', 'N/A')[:60]}..."
                )

        # Section 3: Decision Audit Log
        audit_log = state.get("decision_audit_log", [])
        if audit_log:
            summary_lines.extend([
                "\n## Decision Audit Trail",
                f"Total decisions logged: {len(audit_log)}",
            ])
            for entry in audit_log[:5]:
                summary_lines.append(
                    f"  • {entry['decision_type']}: {entry.get('decision', 'N/A')} "
                    f"(confidence: {entry.get('confidence', 0):.2f})"
                )

        # Section 4: Transparency Metrics
        summary_lines.extend([
            "\n## Transparency Metrics",
            f"  • Phases Explained: {len(reasoning_traces)}/9",
            f"  • Audit Entries: {len(audit_log)}",
            f"  • Confidence Justified: {len(confidence_just)}",
            f"  • Explainability Score: {_calculate_explainability_score(state):.2%}",
        ])

        phase9_summary = "\n".join(summary_lines)

        state.update({
            "phase9_summary": phase9_summary,
            "explainability_score": _calculate_explainability_score(state),
        })

        return state

    return process


def _generate_phase_trace(llm: LLMFn, phase_name: str, *context_items) -> dict:
    """Generate detailed reasoning trace for a phase."""
    context_str = "\n".join([str(item) for item in context_items if item])

    prompt = f"""Generate a concise reasoning trace for {phase_name}:

Context:
{context_str}

Provide:
SUMMARY: [one-line summary of reasoning]
REASONING: [key reasoning steps]
ALTERNATIVES: [considered alternatives]
CONFIDENCE_FACTORS: [factors affecting confidence]"""

    response = llm(prompt)
    return _parse_trace_response(response)


def _parse_trace_response(response: str) -> dict:
    """Parse reasoning trace response."""
    trace = {
        "summary": "",
        "reasoning": [],
        "alternatives": [],
        "confidence_factors": [],
    }

    lines = response.split("\n")
    current_section = None

    for line in lines:
        if line.startswith("SUMMARY:"):
            trace["summary"] = line.split(":", 1)[-1].strip()
        elif line.startswith("REASONING:"):
            current_section = "reasoning"
            reasoning_text = line.split(":", 1)[-1].strip()
            if reasoning_text:
                trace["reasoning"].append(reasoning_text)
        elif line.startswith("ALTERNATIVES:"):
            current_section = "alternatives"
            alt_text = line.split(":", 1)[-1].strip()
            if alt_text:
                trace["alternatives"].append(alt_text)
        elif line.startswith("CONFIDENCE_FACTORS:"):
            current_section = "confidence_factors"
            conf_text = line.split(":", 1)[-1].strip()
            if conf_text:
                trace["confidence_factors"].append(conf_text)
        elif line.strip() and current_section and line.startswith("  "):
            trace[current_section].append(line.strip())

    return trace


def _generate_confidence_justification(
    llm: LLMFn, phase_key: str, confidence: float, state: FullAgentState
) -> dict:
    """Generate justification for a confidence score."""
    prompt = f"""Explain why {phase_key} has {confidence:.2%} confidence:

Context:
- Intent: {state.get('intent', 'N/A')}
- Outcome: {state.get('execution_outcome', 'N/A')}
- Lessons Learned: {', '.join(state.get('lessons_learned', []))}

Provide:
REASONING: [why this confidence level]
SUPPORTING_EVIDENCE: [evidence for confidence]
LIMITING_FACTORS: [factors that reduce confidence]
OVERALL_ASSESSMENT: [is confidence justified]"""

    response = llm(prompt)
    return _parse_justification_response(response)


def _parse_justification_response(response: str) -> dict:
    """Parse confidence justification response."""
    justification = {
        "reasoning": "",
        "evidence": [],
        "limiting_factors": [],
        "assessment": "",
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("REASONING:"):
            justification["reasoning"] = line.split(":", 1)[-1].strip()
        elif line.startswith("SUPPORTING_EVIDENCE:"):
            evidence_text = line.split(":", 1)[-1].strip()
            if evidence_text:
                justification["evidence"].append(evidence_text)
        elif line.startswith("LIMITING_FACTORS:"):
            limiting_text = line.split(":", 1)[-1].strip()
            if limiting_text:
                justification["limiting_factors"].append(limiting_text)
        elif line.startswith("OVERALL_ASSESSMENT:"):
            justification["assessment"] = line.split(":", 1)[-1].strip()

    return justification


def _extract_alternatives(state: FullAgentState) -> list:
    """Extract considered alternatives from state."""
    alternatives = []

    # From Phase 3c Creativity
    if state.get("creative_ideas"):
        alternatives.extend(state.get("creative_ideas", [])[:3])

    # From Phase 8 Recovery
    if state.get("historical_alternatives"):
        historical = state.get("historical_alternatives", {})
        alternatives.extend(historical.get("successful_tools", [])[:2])

    return list(set(alternatives))[:5]


def _calculate_overall_confidence(confidences: dict) -> float:
    """Calculate overall system confidence from individual scores."""
    if not confidences:
        return 0.0

    valid_scores = [v for v in confidences.values() if v > 0]
    if not valid_scores:
        return 0.0

    return sum(valid_scores) / len(valid_scores)


def _calculate_explainability_score(state: FullAgentState) -> float:
    """Calculate how explainable the system's decisions are."""
    score = 0.0
    max_score = 0.0

    # Reasoning traces (max 0.3)
    traces = state.get("reasoning_traces", {})
    if traces:
        score += min(0.3, len(traces) * 0.03)
    max_score += 0.3

    # Confidence justifications (max 0.3)
    just = state.get("confidence_justifications", {})
    if just:
        score += min(0.3, len(just) * 0.075)
    max_score += 0.3

    # Decision audit log (max 0.2)
    audit = state.get("decision_audit_log", [])
    if audit:
        score += min(0.2, len(audit) * 0.04)
    max_score += 0.2

    # Confidence scores present (max 0.2)
    confidence_fields = [
        "tool_selection_confidence",
        "outcome_confidence",
        "phase7_confidence",
        "recovery_confidence",
    ]
    present = sum(1 for f in confidence_fields if state.get(f, 0) > 0)
    if present > 0:
        score += min(0.2, (present / len(confidence_fields)) * 0.2)
    max_score += 0.2

    return score / max_score if max_score > 0 else 0.0
