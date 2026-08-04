"""Phase 8: Error Recovery & Intelligent Retry."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState
from learning.memory_manager import MemoryManager

LLMFn = Callable[[str], str]


def make_error_detection_node(llm: LLMFn):
    """
    Create Phase 8a error detection node.

    Analyzes execution outcome and determines if recovery is needed.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 8a: Error Detection.

        Identifies failures and determines recovery strategy.
        """
        execution_outcome = state.get("execution_outcome", "success")
        failure_analysis = state.get("failure_analysis", {})

        # Determine if recovery is needed
        needs_recovery = execution_outcome in ["failure", "partial"]
        recovery_strategy = _determine_recovery_strategy(
            state, execution_outcome, failure_analysis
        )

        # Analyze failure details
        error_details = _analyze_error_details(llm, state, failure_analysis)

        state.update({
            "recovery_needed": needs_recovery,
            "recovery_strategy": recovery_strategy,
            "error_details": error_details,
            "recovery_attempt_count": 0,
        })

        return state

    return process


def make_retry_orchestration_node(llm: LLMFn, memory_manager: MemoryManager):
    """
    Create Phase 8b retry orchestration node.

    Plans and executes intelligent retry using historical patterns.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 8b: Retry Orchestration.

        Generates retry plan based on Phase 7 insights and error analysis.
        """
        if not state.get("recovery_needed", False):
            state.update({
                "retry_attempted": False,
                "retry_plan": None,
            })
            return state

        input_text = state.get("input_text", "")
        strategy = state.get("recovery_strategy", "alternative_tools")
        error_details = state.get("error_details", {})

        # Get alternative approaches from memory
        similar_executions = memory_manager.find_similar_executions(
            input_text, similarity_threshold=0.3
        )
        historical_alternatives = _extract_alternatives(similar_executions)

        # Generate retry plan
        retry_plan = _generate_retry_plan(
            llm, state, strategy, error_details, historical_alternatives
        )

        state.update({
            "retry_attempted": True,
            "retry_plan": retry_plan,
            "historical_alternatives": historical_alternatives,
            "retry_reasoning": retry_plan.get("reasoning", ""),
        })

        return state

    return process


def make_recovery_execution_node(llm: LLMFn):
    """
    Create Phase 8c recovery execution node.

    Executes retry with adapted tool selection and parameters.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 8c: Recovery Execution.

        Applies retry plan and executes with adapted strategies.
        """
        if not state.get("retry_attempted", False):
            state.update({
                "recovery_executed": False,
                "retry_result": None,
            })
            return state

        retry_plan = state.get("retry_plan", {})
        original_tools = state.get("selected_tools", [])
        alternative_tools = retry_plan.get("alternative_tools", [])

        # Simulate retry execution (in production would actually re-execute)
        retry_result = _simulate_recovery_execution(
            llm, state, original_tools, alternative_tools
        )

        # Compare outcomes
        original_outcome = state.get("execution_outcome", "failure")
        retry_success = _evaluate_retry_success(
            original_outcome, retry_result.get("outcome", "failure")
        )

        state.update({
            "recovery_executed": True,
            "retry_result": retry_result,
            "retry_success": retry_success,
            "retry_outcome": retry_result.get("outcome", "failure"),
            "recovery_confidence": retry_result.get("confidence", 0.0),
        })

        return state

    return process


def make_recovery_summary_node(llm: LLMFn):
    """
    Create Phase 8 summary node.

    Generates comprehensive recovery report.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate summary of Phase 8 error recovery."""
        summary_lines = [
            "=== Phase 8: Error Recovery & Intelligent Retry ===",
        ]

        if not state.get("recovery_needed", False):
            summary_lines.append("Status: No recovery needed - execution successful")
        else:
            summary_lines.extend([
                f"Status: Recovery attempted",
                f"Original Outcome: {state.get('execution_outcome', 'unknown').upper()}",
                f"Recovery Strategy: {state.get('recovery_strategy', 'unknown')}",
            ])

            if state.get("retry_attempted"):
                summary_lines.extend([
                    f"\nRetry Plan:",
                    f"  Original Tools: {', '.join(state.get('selected_tools', []))}",
                ])

                retry_plan = state.get("retry_plan", {})
                if retry_plan.get("alternative_tools"):
                    summary_lines.append(
                        f"  Alternative Tools: {', '.join(retry_plan['alternative_tools'])}"
                    )

                summary_lines.append(
                    f"  Reasoning: {retry_plan.get('reasoning', 'N/A')}"
                )

            if state.get("recovery_executed"):
                summary_lines.extend([
                    f"\nRetry Execution:",
                    f"  Retry Outcome: {state.get('retry_outcome', 'unknown').upper()}",
                    f"  Success: {'✓ YES' if state.get('retry_success') else '✗ NO'}",
                    f"  Confidence: {state.get('recovery_confidence', 0):.2f}",
                ])

                retry_result = state.get("retry_result", {})
                if retry_result.get("improvements"):
                    summary_lines.append(f"\n  Improvements Made:")
                    for improvement in retry_result.get("improvements", [])[:3]:
                        summary_lines.append(f"    • {improvement}")

        phase8_summary = "\n".join(summary_lines)

        state.update({
            "phase8_summary": phase8_summary,
        })

        return state

    return process


def _determine_recovery_strategy(
    state: FullAgentState, outcome: str, failure_analysis: dict
) -> str:
    """Determine the recovery strategy based on failure type."""
    if outcome == "success":
        return "none"

    if outcome == "partial":
        return "enhance_reasoning"

    # For failure, check failure analysis
    analysis = failure_analysis.get("analysis", "")
    if "parameter" in analysis.lower():
        return "adjust_parameters"
    elif "tool" in analysis.lower():
        return "alternative_tools"
    elif "timeout" in analysis.lower():
        return "increase_resources"
    else:
        return "comprehensive_retry"


def _analyze_error_details(
    llm: LLMFn, state: FullAgentState, failure_analysis: dict
) -> dict:
    """Analyze error details to guide recovery."""
    prompt = f"""Analyze this execution failure and provide recovery guidance:

Error Analysis:
{failure_analysis.get('analysis', 'No analysis available')}

Selected Tools: {', '.join(state.get('selected_tools', []))}
Execution Outcome: {state.get('execution_outcome', 'unknown')}

Provide structured analysis in this format:
ROOT_CAUSE: [main cause]
RECOVERY_OPTIONS: [option 1, option 2, option 3]
RISK_LEVEL: [low, medium, high]
RECOMMENDED_ACTION: [specific action]"""

    response = llm(prompt)
    return _parse_error_analysis(response)


def _parse_error_analysis(response: str) -> dict:
    """Parse error analysis response from LLM."""
    analysis = {
        "root_cause": "",
        "recovery_options": [],
        "risk_level": "medium",
        "recommended_action": "",
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ROOT_CAUSE"):
            analysis["root_cause"] = line.split(":", 1)[-1].strip()
        elif line.startswith("RECOVERY_OPTIONS"):
            options_str = line.split(":", 1)[-1].strip()
            # Parse list format
            analysis["recovery_options"] = [
                opt.strip() for opt in options_str.split(",")
            ]
        elif line.startswith("RISK_LEVEL"):
            analysis["risk_level"] = line.split(":", 1)[-1].strip().lower()
        elif line.startswith("RECOMMENDED_ACTION"):
            analysis["recommended_action"] = line.split(":", 1)[-1].strip()

    return analysis


def _extract_alternatives(similar_executions: list) -> dict:
    """Extract alternative approaches from similar executions."""
    alternatives = {
        "successful_tools": [],
        "tool_sequences": [],
        "parameter_patterns": [],
    }

    for memory, _ in similar_executions[:5]:
        if memory.execution_outcome == "success":
            alternatives["successful_tools"].extend(memory.effective_tools)
            alternatives["tool_sequences"].append(memory.effective_tools)
            alternatives["parameter_patterns"].extend(
                memory.improvement_suggestions[:2]
            )

    # Deduplicate
    alternatives["successful_tools"] = list(set(alternatives["successful_tools"]))
    alternatives["parameter_patterns"] = list(
        set(alternatives["parameter_patterns"])
    )

    return alternatives


def _generate_retry_plan(
    llm: LLMFn,
    state: FullAgentState,
    strategy: str,
    error_details: dict,
    historical_alternatives: dict,
) -> dict:
    """Generate detailed retry plan."""
    original_tools = ", ".join(state.get("selected_tools", []))
    root_cause = error_details.get("root_cause", "unknown")
    recommended = error_details.get("recommended_action", "retry with alternatives")

    prompt = f"""Based on this execution failure, generate a specific retry plan:

Original Tools: {original_tools}
Strategy: {strategy}
Root Cause: {root_cause}
Recommended Action: {recommended}

Available Successful Alternatives:
{', '.join(historical_alternatives.get('successful_tools', []))}

Provide plan in this format:
ALTERNATIVE_TOOLS: [tool1, tool2, tool3]
PARAMETER_ADJUSTMENTS: [adjustment1, adjustment2]
EXECUTION_SEQUENCE: [step1 → step2 → step3]
REASONING: [why this should work]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_retry_plan(response)


def _parse_retry_plan(response: str) -> dict:
    """Parse retry plan from LLM response."""
    plan = {
        "alternative_tools": [],
        "parameter_adjustments": [],
        "execution_sequence": [],
        "reasoning": "",
        "confidence": 0.5,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("ALTERNATIVE_TOOLS"):
            tools_str = line.split(":", 1)[-1].strip()
            plan["alternative_tools"] = [
                t.strip() for t in tools_str.split(",") if t.strip()
            ]
        elif line.startswith("PARAMETER_ADJUSTMENTS"):
            adj_str = line.split(":", 1)[-1].strip()
            plan["parameter_adjustments"] = [
                a.strip() for a in adj_str.split(",") if a.strip()
            ]
        elif line.startswith("EXECUTION_SEQUENCE"):
            seq_str = line.split(":", 1)[-1].strip()
            plan["execution_sequence"] = [
                s.strip() for s in seq_str.split("→") if s.strip()
            ]
        elif line.startswith("REASONING"):
            plan["reasoning"] = line.split(":", 1)[-1].strip()
        elif line.startswith("CONFIDENCE"):
            try:
                plan["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                plan["confidence"] = 0.5

    return plan


def _simulate_recovery_execution(
    llm: LLMFn,
    state: FullAgentState,
    original_tools: list,
    alternative_tools: list,
) -> dict:
    """Simulate recovery execution with adapted strategy."""
    prompt = f"""Evaluate this retry execution:

Original Tools: {', '.join(original_tools)}
Alternative Tools: {', '.join(alternative_tools)}
Original Outcome: {state.get('execution_outcome', 'failure')}

Estimate the likely outcome after applying this recovery strategy.

Provide result in this format:
OUTCOME: [success, partial, failure]
IMPROVEMENTS: [improvement1, improvement2, improvement3]
CONFIDENCE: [0.0-1.0]
EXPLANATION: [why this outcome is expected]"""

    response = llm(prompt)
    return _parse_execution_result(response)


def _parse_execution_result(response: str) -> dict:
    """Parse execution result from LLM response."""
    result = {
        "outcome": "partial",
        "improvements": [],
        "confidence": 0.5,
        "explanation": "",
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("OUTCOME"):
            result["outcome"] = line.split(":", 1)[-1].strip().lower()
        elif line.startswith("IMPROVEMENTS"):
            imp_str = line.split(":", 1)[-1].strip()
            result["improvements"] = [
                i.strip() for i in imp_str.split(",") if i.strip()
            ]
        elif line.startswith("CONFIDENCE"):
            try:
                result["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                result["confidence"] = 0.5
        elif line.startswith("EXPLANATION"):
            result["explanation"] = line.split(":", 1)[-1].strip()

    return result


def _evaluate_retry_success(original_outcome: str, retry_outcome: str) -> bool:
    """Determine if retry was successful."""
    outcome_rank = {"failure": 0, "partial": 1, "success": 2}

    original_rank = outcome_rank.get(original_outcome, 0)
    retry_rank = outcome_rank.get(retry_outcome, 0)

    return retry_rank > original_rank
