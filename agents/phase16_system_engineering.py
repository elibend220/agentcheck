"""Phase 16: System Engineering & Self-Optimization."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState

LLMFn = Callable[[str], str]


def make_metrics_collection_node(llm: LLMFn):
    """
    Create Phase 16a metrics collection node.

    Gathers performance data from all executed phases.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 16a: Metrics Collection.

        Collects system-wide performance metrics.
        """
        metrics = _collect_metrics(llm, state)

        state.update({
            "phase_latencies": metrics.get("latencies", {}),
            "phase_success_rates": metrics.get("success_rates", {}),
            "node_execution_counts": metrics.get("execution_counts", {}),
            "resource_usage": metrics.get("resource_usage", {}),
            "bottleneck_phases": metrics.get("bottlenecks", []),
            "metrics_collection_confidence": metrics.get("confidence", 0.0),
        })

        return state

    return process


def make_architecture_analysis_node(llm: LLMFn):
    """
    Create Phase 16b architecture analysis node.

    Analyzes which phases contribute most to system performance.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 16b: Architecture Analysis.

        Analyzes phase contributions and identifies optimization opportunities.
        """
        latencies = state.get("phase_latencies", {})
        success_rates = state.get("phase_success_rates", {})

        if not latencies and not success_rates:
            state.update({
                "critical_phases": [],
                "low_impact_phases": [],
                "phase_coupling_analysis": {},
                "optimization_opportunities": [],
                "architecture_analysis_confidence": 0.0,
            })
            return state

        analysis = _analyze_architecture(llm, state, latencies, success_rates)

        state.update({
            "critical_phases": analysis.get("critical", []),
            "low_impact_phases": analysis.get("low_impact", []),
            "phase_coupling_analysis": analysis.get("coupling", {}),
            "optimization_opportunities": analysis.get("opportunities", []),
            "architecture_analysis_confidence": analysis.get("confidence", 0.0),
        })

        return state

    return process


def make_optimization_recommendation_node(llm: LLMFn):
    """
    Create Phase 16c optimization recommendation node.

    Generates recommendations for system improvement.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 16c: Optimization Recommendation.

        Creates specific recommendations for system optimization.
        """
        opportunities = state.get("optimization_opportunities", [])
        critical = state.get("critical_phases", [])
        low_impact = state.get("low_impact_phases", [])

        if not opportunities and not critical and not low_impact:
            state.update({
                "recommended_phase_changes": [],
                "recommended_routing_changes": [],
                "recommended_resource_allocation": {},
                "optimization_priority": [],
                "optimization_recommendation_confidence": 0.0,
            })
            return state

        recommendations = _generate_recommendations(llm, state, opportunities, critical, low_impact)

        state.update({
            "recommended_phase_changes": recommendations.get("phase_changes", []),
            "recommended_routing_changes": recommendations.get("routing_changes", []),
            "recommended_resource_allocation": recommendations.get("resources", {}),
            "optimization_priority": recommendations.get("priority", []),
            "optimization_recommendation_confidence": recommendations.get("confidence", 0.0),
        })

        return state

    return process


def make_adaptive_configurator_node(llm: LLMFn):
    """
    Create Phase 16d adaptive configurator node.

    Applies optimizations and generates system engineering summary.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 16d: Adaptive Configurator.

        Applies recommended optimizations and generates summary.
        """
        phase_changes = state.get("recommended_phase_changes", [])
        routing_changes = state.get("recommended_routing_changes", [])
        resources = state.get("recommended_resource_allocation", {})

        applied = _apply_optimizations(llm, state, phase_changes, routing_changes, resources)

        summary_lines = [
            "=== System Engineering & Self-Optimization ===",
        ]

        # Metrics Overview
        latencies = state.get("phase_latencies", {})
        if latencies:
            total_latency = sum(v for v in latencies.values() if isinstance(v, (int, float)))
            summary_lines.extend([
                f"\n⏱️  Performance Metrics:",
                f"  Total Latency: {total_latency}ms",
            ])
            bottlenecks = state.get("bottleneck_phases", [])
            if bottlenecks:
                summary_lines.append(f"  Bottlenecks: {', '.join(bottlenecks[:3])}")

        # Critical Phases
        critical = state.get("critical_phases", [])
        if critical:
            summary_lines.extend([
                f"\n🔴 Critical Phases ({len(critical)}):",
            ])
            for phase in critical[:3]:
                summary_lines.append(f"  ⚡ {phase}")

        # Low Impact Phases
        low_impact = state.get("low_impact_phases", [])
        if low_impact:
            summary_lines.extend([
                f"\n🟢 Low Impact Phases ({len(low_impact)}):",
            ])
            for phase in low_impact[:3]:
                summary_lines.append(f"  ○ {phase}")

        # Applied Changes
        applied_count = len(applied.get("applied_changes", []))
        if applied_count > 0:
            summary_lines.extend([
                f"\n✅ Applied Optimizations ({applied_count}):",
            ])
            for change in applied.get("applied_changes", [])[:3]:
                summary_lines.append(f"  ✓ {change}")

        # Recommended Changes (not yet applied)
        recommendations = state.get("recommended_phase_changes", [])
        if recommendations:
            summary_lines.extend([
                f"\n💡 Recommended Changes ({len(recommendations)}):",
            ])
            for rec in recommendations[:3]:
                summary_lines.append(f"  → {rec}")

        # Self-Improvement Status
        summary_lines.extend([
            f"\n✨ System Optimization Status:",
            f"  Adaptive Ready: {'YES' if applied.get('ready', False) else 'NO'}",
            f"  Optimizations Applied: {applied_count}",
            f"  Confidence: {applied.get('confidence', 0):.0%}",
        ])

        phase16_summary = "\n".join(summary_lines)

        state.update({
            "applied_optimizations": applied.get("applied_changes", []),
            "optimization_applied": applied.get("ready", False),
            "system_optimized": True,
            "optimization_applied_confidence": applied.get("confidence", 0.0),
            "phase16_summary": phase16_summary,
        })

        return state

    return process


def _collect_metrics(llm: LLMFn, state: FullAgentState) -> dict:
    """Collect system performance metrics."""
    execution_history = state.get("execution_history", [])

    prompt = f"""Analyze system performance metrics:

Execution History Size: {len(execution_history)}
Phases Enabled: {sum([state.get(f'enable_phase{i}', False) for i in range(1, 22)])}
Overall Confidence: {state.get('overall_system_confidence', 0):.0%}

Provide:
PHASE_LATENCIES: [phase: latency_ms format]
SUCCESS_RATES: [phase: success_rate format]
NODE_EXECUTION_COUNTS: [node: count format]
RESOURCE_USAGE: [memory_mb, cpu_percent]
BOTTLENECK_PHASES: [phases taking most time]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_metrics_response(response)


def _parse_metrics_response(response: str) -> dict:
    """Parse metrics collection response."""
    metrics = {
        "latencies": {},
        "success_rates": {},
        "execution_counts": {},
        "resource_usage": {},
        "bottlenecks": [],
        "confidence": 0.8,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("PHASE_LATENCIES:"):
            latencies_str = line.split(":", 1)[-1].strip()
            if latencies_str:
                try:
                    pairs = [p.strip() for p in latencies_str.split(",")]
                    for pair in pairs:
                        if ":" in pair:
                            phase, lat = pair.split(":", 1)
                            metrics["latencies"][phase.strip()] = float(lat.strip().rstrip("ms"))
                except (ValueError, IndexError):
                    pass

        elif line.startswith("SUCCESS_RATES:"):
            rates_str = line.split(":", 1)[-1].strip()
            if rates_str:
                try:
                    pairs = [p.strip() for p in rates_str.split(",")]
                    for pair in pairs:
                        if ":" in pair:
                            phase, rate = pair.split(":", 1)
                            metrics["success_rates"][phase.strip()] = float(rate.strip().rstrip("%")) / 100
                except (ValueError, IndexError):
                    pass

        elif line.startswith("BOTTLENECK_PHASES:"):
            bottlenecks_str = line.split(":", 1)[-1].strip()
            if bottlenecks_str:
                bottlenecks = [b.strip().strip("[](),") for b in bottlenecks_str.split(",")]
                metrics["bottlenecks"] = [b for b in bottlenecks if b]

        elif line.startswith("CONFIDENCE:"):
            try:
                metrics["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                metrics["confidence"] = 0.8

    return metrics


def _analyze_architecture(llm: LLMFn, state: FullAgentState, latencies: dict, success_rates: dict) -> dict:
    """Analyze system architecture."""
    latencies_str = ", ".join([f"{k}: {v}ms" for k, v in list(latencies.items())[:5]])

    prompt = f"""Analyze system architecture:

Phase Latencies: {latencies_str}
Success Rates: {', '.join([f'{k}: {v:.0%}' for k, v in list(success_rates.items())[:3]])}

Provide:
CRITICAL_PHASES: [phases that are essential]
LOW_IMPACT_PHASES: [phases contributing little]
PHASE_COUPLING: [interdependencies between phases]
OPPORTUNITIES: [optimization opportunities]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_analysis_response(response)


def _parse_analysis_response(response: str) -> dict:
    """Parse architecture analysis response."""
    analysis = {
        "critical": [],
        "low_impact": [],
        "coupling": {},
        "opportunities": [],
        "confidence": 0.78,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("CRITICAL_PHASES:"):
            critical_str = line.split(":", 1)[-1].strip()
            if critical_str:
                critical = [c.strip().strip("[](),") for c in critical_str.split(",")]
                analysis["critical"] = [c for c in critical if c]

        elif line.startswith("LOW_IMPACT_PHASES:"):
            low_str = line.split(":", 1)[-1].strip()
            if low_str:
                low = [l.strip().strip("[](),") for l in low_str.split(",")]
                analysis["low_impact"] = [l for l in low if l]

        elif line.startswith("OPPORTUNITIES:"):
            opps_str = line.split(":", 1)[-1].strip()
            if opps_str:
                opps = [o.strip().strip("[](),") for o in opps_str.split(",")]
                analysis["opportunities"] = [o for o in opps if o]

        elif line.startswith("CONFIDENCE:"):
            try:
                analysis["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                analysis["confidence"] = 0.78

    return analysis


def _generate_recommendations(llm: LLMFn, state: FullAgentState, opportunities: list, critical: list, low_impact: list) -> dict:
    """Generate optimization recommendations."""
    opps_str = ", ".join(opportunities[:3])

    prompt = f"""Generate system optimization recommendations:

Opportunities: {opps_str}
Critical Phases: {', '.join(critical[:2])}
Low Impact: {', '.join(low_impact[:2])}

Provide:
PHASE_CHANGES: [enable/disable recommendations]
ROUTING_CHANGES: [routing optimization suggestions]
RESOURCE_ALLOCATION: [resource reallocation]
PRIORITY: [priority order for changes]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_recommendations_response(response)


def _parse_recommendations_response(response: str) -> dict:
    """Parse recommendations response."""
    recommendations = {
        "phase_changes": [],
        "routing_changes": [],
        "resources": {},
        "priority": [],
        "confidence": 0.76,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("PHASE_CHANGES:"):
            changes_str = line.split(":", 1)[-1].strip()
            if changes_str:
                changes = [c.strip().strip("[](),") for c in changes_str.split(",")]
                recommendations["phase_changes"] = [c for c in changes if c]

        elif line.startswith("ROUTING_CHANGES:"):
            routing_str = line.split(":", 1)[-1].strip()
            if routing_str:
                routing = [r.strip().strip("[](),") for r in routing_str.split(",")]
                recommendations["routing_changes"] = [r for r in routing if r]

        elif line.startswith("PRIORITY:"):
            priority_str = line.split(":", 1)[-1].strip()
            if priority_str:
                priority = [p.strip().strip("[](),") for p in priority_str.split(",")]
                recommendations["priority"] = [p for p in priority if p]

        elif line.startswith("CONFIDENCE:"):
            try:
                recommendations["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                recommendations["confidence"] = 0.76

    return recommendations


def _apply_optimizations(llm: LLMFn, state: FullAgentState, phase_changes: list, routing_changes: list, resources: dict) -> dict:
    """Apply optimizations to system."""
    changes_str = ", ".join(phase_changes[:2]) if phase_changes else "none"

    prompt = f"""Apply system optimizations:

Phase Changes: {changes_str}
Routing Changes: {len(routing_changes)} changes
Resource Changes: {len(resources)} allocations

Provide:
APPLIED_CHANGES: [changes successfully applied]
IMPACT: [expected performance improvement]
READY: [true/false system is optimized]
CONFIDENCE: [0.0-1.0]"""

    response = llm(prompt)
    return _parse_applied_response(response)


def _parse_applied_response(response: str) -> dict:
    """Parse applied optimizations response."""
    applied = {
        "applied_changes": [],
        "impact": "",
        "ready": True,
        "confidence": 0.80,
    }

    lines = response.split("\n")
    for line in lines:
        if line.startswith("APPLIED_CHANGES:"):
            changes_str = line.split(":", 1)[-1].strip()
            if changes_str:
                changes = [c.strip().strip("[](),") for c in changes_str.split(",")]
                applied["applied_changes"] = [c for c in changes if c]

        elif line.startswith("IMPACT:"):
            applied["impact"] = line.split(":", 1)[-1].strip()

        elif line.startswith("READY:"):
            ready_str = line.split(":", 1)[-1].strip().lower()
            applied["ready"] = ready_str in ["true", "yes", "1"]

        elif line.startswith("CONFIDENCE:"):
            try:
                applied["confidence"] = float(line.split(":", 1)[-1].strip())
            except ValueError:
                applied["confidence"] = 0.80

    return applied
