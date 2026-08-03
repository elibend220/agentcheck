"""Quantum metrics and performance analysis."""

from __future__ import annotations

from typing import Optional, Any
import numpy as np
from quantum.principles import QuantumState, QuantumPhase5State


def compute_quantum_metrics(
    quantum_state: QuantumState,
    tool_configurations: Optional[list[list[str]]] = None
) -> dict[str, Any]:
    """
    Compute comprehensive metrics for quantum state.

    Returns dict with entropy, purity, measurement probabilities, etc.
    """
    metrics = {
        "entropy": quantum_state.get_entropy(),
        "purity": quantum_state.get_purity(),
        "is_pure": quantum_state.is_pure(),
        "is_maximally_entangled": quantum_state.is_maximally_entangled(),
        "temperature": quantum_state.temperature,
        "iteration": quantum_state.iteration,
    }

    # Probability distribution
    probs = quantum_state.get_probability_distribution()
    metrics["mean_probability"] = float(np.mean(list(probs.values())))
    metrics["max_probability"] = float(np.max(list(probs.values())) if probs else 0)
    metrics["min_probability"] = float(np.min(list(probs.values())) if probs else 0)
    metrics["probability_std"] = float(np.std(list(probs.values())))

    # Top tools
    top_tools = quantum_state.get_top_tools(k=5)
    metrics["top_tools"] = [
        {"tool_id": tid, "probability": prob}
        for tid, prob in top_tools
    ]

    # Configuration metrics
    if tool_configurations:
        from quantum.principles import QuantumEnergyEvaluator
        from tools.schema import ToolRegistry

        registry = None
        evaluator = QuantumEnergyEvaluator(registry)

        config_metrics = []
        for config in tool_configurations:
            try:
                energy = evaluator.evaluate(config)
                config_metrics.append({
                    "config": config,
                    "energy": energy,
                    "size": len(config)
                })
            except:
                pass

        if config_metrics:
            metrics["configurations"] = config_metrics
            metrics["best_config_energy"] = min(
                c["energy"] for c in config_metrics
            )

    return metrics


def compare_phase4_vs_phase5(
    phase4_result: dict[str, Any],
    phase5_result: dict[str, Any],
    selected_tools_phase4: list[str],
    selected_tools_phase5: list[str]
) -> dict[str, Any]:
    """
    Compare Phase 4 (classical) vs Phase 5 (quantum-inspired) results.

    Metrics: coverage, efficiency, diversity, execution time, etc.
    """
    from quantum.principles import QuantumEnergyEvaluator

    # Create a minimal registry-like object for evaluation
    class MinimalRegistry:
        def get(self, tool_id):
            return None

    evaluator = QuantumEnergyEvaluator(MinimalRegistry())

    comparison = {
        "phase4": {
            "selected_tools": selected_tools_phase4,
            "tool_count": len(selected_tools_phase4),
            "energy": evaluator.evaluate(selected_tools_phase4),
        },
        "phase5": {
            "selected_tools": selected_tools_phase5,
            "tool_count": len(selected_tools_phase5),
            "energy": evaluator.evaluate(selected_tools_phase5),
        },
    }

    # Analyze improvements
    phase4_energy = comparison["phase4"]["energy"]
    phase5_energy = comparison["phase5"]["energy"]

    if phase4_energy != float("inf") and phase5_energy != float("inf"):
        energy_improvement = (phase4_energy - phase5_energy) / max(abs(phase4_energy), 1e-6)
        comparison["energy_improvement_ratio"] = float(energy_improvement)
    else:
        comparison["energy_improvement_ratio"] = 0.0

    # Tool count efficiency
    phase4_count = len(selected_tools_phase4)
    phase5_count = len(selected_tools_phase5)
    comparison["efficiency_improvement"] = float(
        (phase4_count - phase5_count) / max(phase4_count, 1)
    )

    # Coverage metrics
    phase4_coverage = _compute_coverage(selected_tools_phase4)
    phase5_coverage = _compute_coverage(selected_tools_phase5)
    comparison["coverage"] = {
        "phase4": phase4_coverage,
        "phase5": phase5_coverage,
        "improvement": phase5_coverage - phase4_coverage,
    }

    # Diversity metrics
    phase4_diversity = _compute_diversity(selected_tools_phase4)
    phase5_diversity = _compute_diversity(selected_tools_phase5)
    comparison["diversity"] = {
        "phase4": phase4_diversity,
        "phase5": phase5_diversity,
        "improvement": phase5_diversity - phase4_diversity,
    }

    # Execution results
    phase4_exec_time = phase4_result.get("execution_time", 0)
    phase5_exec_time = phase5_result.get("execution_time", 0)

    if phase4_exec_time > 0 and phase5_exec_time > 0:
        comparison["execution_time_ratio"] = phase5_exec_time / phase4_exec_time
    else:
        comparison["execution_time_ratio"] = 1.0

    # Error metrics
    phase4_errors = len(phase4_result.get("error_log", []))
    phase5_errors = len(phase5_result.get("error_log", []))
    comparison["errors"] = {
        "phase4": phase4_errors,
        "phase5": phase5_errors,
        "improvement": (phase4_errors - phase5_errors) / max(phase4_errors, 1),
    }

    # Overall score
    comparison["overall_score"] = _compute_overall_score(
        phase4_energy, phase5_energy,
        phase4_count, phase5_count,
        phase4_errors, phase5_errors
    )

    return comparison


def _compute_coverage(tools: list[str]) -> float:
    """Estimate coverage from tool count (placeholder)."""
    return min(len(tools) / 10.0, 1.0)


def _compute_diversity(tools: list[str]) -> float:
    """Estimate diversity as normalized tool count."""
    return min(len(set(tools)) / 5.0, 1.0)


def _compute_overall_score(
    phase4_energy: float,
    phase5_energy: float,
    phase4_count: int,
    phase5_count: int,
    phase4_errors: int,
    phase5_errors: int
) -> float:
    """
    Compute overall performance score.

    Returns value in [0, 1] where 1 = perfect improvement.
    """
    score_components = []

    # Energy improvement (40% weight)
    if phase4_energy != float("inf") and phase5_energy != float("inf"):
        energy_score = min(
            1.0,
            max(0.0, (phase4_energy - phase5_energy) / max(abs(phase4_energy), 1))
        )
        score_components.append(energy_score * 0.4)

    # Efficiency improvement (30% weight)
    if phase4_count > 0:
        efficiency_score = (phase4_count - phase5_count) / phase4_count
        score_components.append(max(0.0, min(efficiency_score, 1.0)) * 0.3)

    # Error reduction (30% weight)
    if phase4_errors > 0:
        error_score = (phase4_errors - phase5_errors) / phase4_errors
        score_components.append(max(0.0, min(error_score, 1.0)) * 0.3)
    elif phase5_errors == 0:
        score_components.append(0.3)

    return float(np.sum(score_components)) if score_components else 0.5


def analyze_quantum_trajectory(
    history: list[dict],
) -> dict[str, Any]:
    """
    Analyze quantum state evolution over iterations.

    Useful for understanding convergence behavior.
    """
    if not history:
        return {}

    iterations = [h.get("iteration", i) for i, h in enumerate(history)]
    temperatures = [h.get("temperature", 1.0) for h in history]
    energies = [h.get("best_energy", float("inf")) for h in history]
    purities = [h.get("purity", 0.5) for h in history]
    entropies = [h.get("entropy", 1.0) for h in history]

    analysis = {
        "total_iterations": len(history),
        "final_temperature": temperatures[-1] if temperatures else 1.0,
        "temperature_trajectory": {
            "initial": temperatures[0] if temperatures else 1.0,
            "final": temperatures[-1] if temperatures else 0.01,
            "mean": float(np.mean(temperatures)) if temperatures else 0.5,
            "std": float(np.std(temperatures)) if temperatures else 0.0,
        },
        "energy_trajectory": {
            "initial": energies[0] if energies else float("inf"),
            "final": energies[-1] if energies else 0.0,
            "min": float(np.min([e for e in energies if e != float("inf")])) if energies else 0.0,
            "improvement": (energies[0] - energies[-1]) if energies else 0.0,
        },
        "purity_trajectory": {
            "initial": purities[0] if purities else 0.5,
            "final": purities[-1] if purities else 0.5,
            "mean": float(np.mean(purities)) if purities else 0.5,
        },
        "entropy_trajectory": {
            "initial": entropies[0] if entropies else 1.0,
            "final": entropies[-1] if entropies else 0.0,
            "mean": float(np.mean(entropies)) if entropies else 0.5,
        },
    }

    # Compute convergence rate
    if len(energies) > 1:
        energy_decreases = [
            max(0, energies[i] - energies[i + 1])
            for i in range(len(energies) - 1)
        ]
        analysis["convergence_rate"] = float(
            np.sum(energy_decreases) / len(energies)
        )

    return analysis


def get_quantum_summary(
    quantum_state: QuantumState,
    phase5_state: Optional[QuantumPhase5State] = None
) -> str:
    """
    Generate human-readable summary of quantum state.

    Useful for logging and reporting.
    """
    lines = []

    lines.append("=== Quantum State Summary ===")
    lines.append(f"Temperature: {quantum_state.temperature:.4f}")
    lines.append(f"Iteration: {quantum_state.iteration}")
    lines.append(f"Entropy: {quantum_state.get_entropy():.4f}")
    lines.append(f"Purity: {quantum_state.get_purity():.4f}")
    lines.append(f"Pure State: {quantum_state.is_pure()}")
    lines.append(f"Maximally Entangled: {quantum_state.is_maximally_entangled()}")

    # Top tools
    top_tools = quantum_state.get_top_tools(k=3)
    if top_tools:
        lines.append("\nTop Tools:")
        for tool_id, prob in top_tools:
            lines.append(f"  {tool_id}: {prob:.4f}")

    # Probability stats
    probs = quantum_state.get_probability_distribution()
    if probs:
        lines.append(f"\nProbability Stats:")
        lines.append(f"  Mean: {np.mean(list(probs.values())):.4f}")
        lines.append(f"  Max: {np.max(list(probs.values())):.4f}")
        lines.append(f"  Min: {np.min(list(probs.values())):.4f}")

    if phase5_state:
        lines.append("\nPhase 5 Metrics:")
        if phase5_state.quantum_metrics:
            for key, value in phase5_state.quantum_metrics.items():
                lines.append(f"  {key}: {value}")

    return "\n".join(lines)
