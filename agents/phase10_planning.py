"""Phase 10: Autonomous Planning & Goal Decomposition - Multi-step planning with adaptation."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_goal_decomposition_node(llm: LLMFn):
    """
    Create Phase 10a goal decomposition node.

    Breaks down high-level goals into actionable subgoals.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 10a: Goal Decomposition.

        Converts intent into hierarchical goal structure.
        """
        intent = state.get("intent", "")
        if not intent:
            state.update({
                "primary_goal": None,
                "subgoals": [],
                "goal_hierarchy": {},
            })
            return state

        # Generate goal decomposition
        goal_decomposition = _decompose_goal(llm, intent, state)

        state.update({
            "primary_goal": goal_decomposition.get("primary_goal", ""),
            "subgoals": goal_decomposition.get("subgoals", []),
            "goal_hierarchy": goal_decomposition.get("hierarchy", {}),
        })

        return state

    return process


def make_plan_generation_node(llm: LLMFn):
    """
    Create Phase 10b plan generation node.

    Generates detailed execution plans with resource allocation.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 10b: Plan Generation.

        Creates step-by-step execution plan with dependencies.
        """
        subgoals = state.get("subgoals", [])
        if not subgoals:
            state.update({
                "execution_plan": [],
                "plan_steps": 0,
                "critical_path": [],
            })
            return state

        # Generate execution plan
        execution_plan = _generate_execution_plan(llm, state, subgoals)

        state.update({
            "execution_plan": execution_plan.get("steps", []),
            "plan_steps": len(execution_plan.get("steps", [])),
            "critical_path": execution_plan.get("critical_path", []),
            "plan_estimated_duration": execution_plan.get("estimated_duration", 0),
            "plan_resource_requirements": execution_plan.get("resources", {}),
        })

        return state

    return process


def make_plan_verification_node(llm: LLMFn):
    """
    Create Phase 10c plan verification node.

    Validates plan feasibility and identifies risks.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 10c: Plan Verification.

        Analyzes plan for feasibility, risks, and contingencies.
        """
        execution_plan = state.get("execution_plan", [])
        if not execution_plan:
            state.update({
                "plan_feasibility": 0.0,
                "plan_risks": [],
                "contingencies": [],
                "plan_valid": False,
            })
            return state

        # Verify plan
        verification_result = _verify_plan(llm, state, execution_plan)

        state.update({
            "plan_feasibility": verification_result.get("feasibility", 0.0),
            "plan_risks": verification_result.get("risks", []),
            "contingencies": verification_result.get("contingencies", []),
            "plan_valid": verification_result.get("valid", False),
            "verification_confidence": verification_result.get("confidence", 0.5),
        })

        return state

    return process


def make_planning_summary_node(llm: LLMFn):
    """
    Create Phase 10d planning summary node.

    Generates comprehensive planning report.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate comprehensive planning summary."""
        summary_lines = [
            "=== Phase 10: Autonomous Planning & Goal Decomposition ===",
        ]

        # Primary goal
        if state.get("primary_goal"):
            summary_lines.extend([
                f"\nPrimary Goal: {state.get('primary_goal')}",
            ])

        # Subgoals
        subgoals = state.get("subgoals", [])
        if subgoals:
            summary_lines.extend([
                f"\nSubgoals ({len(subgoals)}):",
            ])
            for i, subgoal in enumerate(subgoals[:5], 1):
                summary_lines.append(f"  {i}. {subgoal}")

        # Execution Plan
        plan_steps = state.get("plan_steps", 0)
        if plan_steps > 0:
            summary_lines.extend([
                f"\nExecution Plan: {plan_steps} steps",
                f"Estimated Duration: {state.get('plan_estimated_duration', 0)} units",
            ])

            critical_path = state.get("critical_path", [])
            if critical_path:
                summary_lines.extend([
                    f"Critical Path ({len(critical_path)} steps):",
                ])
                for step in critical_path[:3]:
                    summary_lines.append(f"  → {step}")

        # Plan Verification
        summary_lines.extend([
            f"\nPlan Verification:",
            f"  Feasibility: {state.get('plan_feasibility', 0):.2%}",
            f"  Valid: {'✓ YES' if state.get('plan_valid') else '✗ NO'}",
            f"  Confidence: {state.get('verification_confidence', 0):.2f}",
        ])

        # Risks and Contingencies
        risks = state.get("plan_risks", [])
        if risks:
            summary_lines.extend([
                f"\nIdentified Risks ({len(risks)}):",
            ])
            for risk in risks[:3]:
                summary_lines.append(f"  ⚠ {risk}")

        contingencies = state.get("contingencies", [])
        if contingencies:
            summary_lines.extend([
                f"\nContingency Plans ({len(contingencies)}):",
            ])
            for contingency in contingencies[:2]:
                summary_lines.append(f"  • {contingency}")

        # Resource Requirements
        resources = state.get("plan_resource_requirements", {})
        if resources:
            summary_lines.extend([
                f"\nResource Requirements:",
            ])
            for resource, amount in list(resources.items())[:3]:
                summary_lines.append(f"  • {resource}: {amount}")

        phase10_summary = "\n".join(summary_lines)

        state.update({
            "phase10_summary": phase10_summary,
        })

        return state

    return process


def _decompose_goal(llm: LLMFn, intent: str, state: FullAgentState) -> dict:
    """Decompose high-level goal into subgoals."""
    prompt = f"""Decompose this goal into actionable subgoals:

Goal: {intent}

Context:
- Available Tools: {', '.join(state.get('selected_tools', []))}
- Knowledge: {state.get('knowledge_summary', 'General knowledge')}

Provide:
PRIMARY_GOAL: [main objective]
SUBGOALS: [subgoal1, subgoal2, subgoal3, ...]
HIERARCHY: [how subgoals relate to primary goal]
DEPENDENCIES: [which subgoals depend on others]"""

    response = llm(prompt)
    return _parse_decomposition_response(response)


def _parse_decomposition_response(response: str) -> dict:
    """Parse goal decomposition response."""
    decomposition = {
        "primary_goal": "",
        "subgoals": [],
        "hierarchy": {},
        "dependencies": [],
    }

    lines = response.split("\n")
    current_section = None

    for line in lines:
        if line.startswith("PRIMARY_GOAL:"):
            decomposition["primary_goal"] = line.split(":", 1)[-1].strip()
        elif line.startswith("SUBGOALS:"):
            current_section = "subgoals"
            subgoals_str = line.split(":", 1)[-1].strip()
            if subgoals_str:
                decomposition["subgoals"].append(subgoals_str)
        elif line.startswith("HIERARCHY:"):
            current_section = "hierarchy"
            hierarchy_str = line.split(":", 1)[-1].strip()
            if hierarchy_str:
                decomposition["hierarchy"] = {"structure": hierarchy_str}
        elif line.startswith("DEPENDENCIES:"):
            current_section = "dependencies"
            deps_str = line.split(":", 1)[-1].strip()
            if deps_str:
                decomposition["dependencies"].append(deps_str)
        elif line.strip() and current_section == "subgoals" and line.startswith("  "):
            decomposition["subgoals"].append(line.strip().lstrip("- "))

    return decomposition


def _generate_execution_plan(
    llm: LLMFn, state: FullAgentState, subgoals: list
) -> dict:
    """Generate detailed execution plan."""
    subgoals_str = "\n".join([f"  {i+1}. {sg}" for i, sg in enumerate(subgoals[:5])])

    prompt = f"""Create a detailed execution plan for these subgoals:

{subgoals_str}

Available Tools: {', '.join(state.get('selected_tools', []))}
Tool Selection Confidence: {state.get('tool_selection_confidence', 0):.2%}

Provide:
EXECUTION_STEPS: [step1, step2, step3, ...]
CRITICAL_PATH: [path determining minimum duration]
ESTIMATED_DURATION: [time units needed]
RESOURCE_REQUIREMENTS: [resources needed for each step]
DEPENDENCIES: [step dependencies]
PARALLELIZABLE: [steps that can run in parallel]"""

    response = llm(prompt)
    return _parse_plan_response(response)


def _parse_plan_response(response: str) -> dict:
    """Parse execution plan response."""
    plan = {
        "steps": [],
        "critical_path": [],
        "estimated_duration": 0,
        "resources": {},
        "dependencies": [],
        "parallelizable": [],
    }

    lines = response.split("\n")
    current_section = None

    for line in lines:
        if line.startswith("EXECUTION_STEPS:"):
            current_section = "steps"
            steps_str = line.split(":", 1)[-1].strip()
            if steps_str:
                plan["steps"].append(steps_str)
        elif line.startswith("CRITICAL_PATH:"):
            current_section = "critical_path"
            path_str = line.split(":", 1)[-1].strip()
            if path_str:
                plan["critical_path"].append(path_str)
        elif line.startswith("ESTIMATED_DURATION:"):
            duration_str = line.split(":", 1)[-1].strip()
            try:
                plan["estimated_duration"] = int(duration_str.split()[0])
            except (ValueError, IndexError):
                plan["estimated_duration"] = 0
        elif line.startswith("RESOURCE_REQUIREMENTS:"):
            current_section = "resources"
            resources_str = line.split(":", 1)[-1].strip()
            if resources_str:
                plan["resources"]["initial"] = resources_str
        elif line.startswith("DEPENDENCIES:"):
            current_section = "dependencies"
            deps_str = line.split(":", 1)[-1].strip()
            if deps_str:
                plan["dependencies"].append(deps_str)
        elif line.startswith("PARALLELIZABLE:"):
            current_section = "parallelizable"
            para_str = line.split(":", 1)[-1].strip()
            if para_str:
                plan["parallelizable"].append(para_str)
        elif line.strip() and current_section and line.startswith("  "):
            item = line.strip().lstrip("- ")
            if current_section == "steps":
                plan["steps"].append(item)
            elif current_section == "critical_path":
                plan["critical_path"].append(item)
            elif current_section == "dependencies":
                plan["dependencies"].append(item)
            elif current_section == "parallelizable":
                plan["parallelizable"].append(item)

    return plan


def _verify_plan(llm: LLMFn, state: FullAgentState, plan: list) -> dict:
    """Verify plan feasibility and identify risks."""
    plan_str = "\n".join([f"  {i+1}. {step}" for i, step in enumerate(plan[:5])])

    prompt = f"""Verify this execution plan for feasibility and risks:

Plan Steps:
{plan_str}

Feasibility Factors:
- Tool Availability: Available
- Resource Constraints: {state.get('plan_resource_requirements', {})}
- Time Constraints: Unconstrained
- Execution History: {state.get('similar_past_executions', 0)} similar tasks

Provide:
FEASIBILITY: [0.0-1.0 confidence]
RISKS: [risk1, risk2, risk3]
CONTINGENCIES: [contingency1, contingency2]
VALID: [true/false]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_verification_response(response)


def _parse_verification_response(response: str) -> dict:
    """Parse plan verification response."""
    verification = {
        "feasibility": 0.5,
        "risks": [],
        "contingencies": [],
        "valid": False,
        "confidence": 0.5,
    }

    lines = response.split("\n")
    current_section = None

    for line in lines:
        if line.startswith("FEASIBILITY:"):
            try:
                verification["feasibility"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                verification["feasibility"] = 0.5
        elif line.startswith("RISKS:"):
            current_section = "risks"
            risks_str = line.split(":", 1)[-1].strip()
            if risks_str:
                verification["risks"].append(risks_str)
        elif line.startswith("CONTINGENCIES:"):
            current_section = "contingencies"
            cont_str = line.split(":", 1)[-1].strip()
            if cont_str:
                verification["contingencies"].append(cont_str)
        elif line.startswith("VALID:"):
            valid_str = line.split(":", 1)[-1].strip().lower()
            verification["valid"] = valid_str in ["true", "yes", "1"]
        elif line.startswith("CONFIDENCE:"):
            try:
                verification["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                verification["confidence"] = 0.5
        elif line.strip() and current_section and line.startswith("  "):
            item = line.strip().lstrip("- ")
            if current_section == "risks":
                verification["risks"].append(item)
            elif current_section == "contingencies":
                verification["contingencies"].append(item)

    return verification
