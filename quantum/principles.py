"""Core quantum-inspired principles and data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Any
import numpy as np
from enum import Enum


class QuantumMeasurementType(Enum):
    """Measurement strategies for collapsing superposition."""
    PROBABILISTIC = "probabilistic"  # Sample per |ψ|²
    DETERMINISTIC = "deterministic"  # Always highest probability
    THRESHOLD = "threshold"  # Above-average probability
    WEIGHTED = "weighted"  # Weighted random selection


@dataclass
class QuantumSnapshot:
    """Snapshot of quantum state at a specific iteration."""
    iteration: int
    amplitudes: dict[str, complex]
    marked_count: int = 0
    amplification_factor: float = 1.0
    temperature: float = 1.0
    convergence_metric: float = 0.0


@dataclass
class QuantumState:
    """Complete quantum state representation."""
    tool_amplitudes: dict[str, complex]
    parameter_couplings: Optional[dict] = None
    temperature: float = 1.0
    iteration: int = 0
    history: list[QuantumSnapshot] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def get_probability_distribution(self) -> dict[str, float]:
        """Compute probability |ψ|² for each tool."""
        return {
            tid: abs(amp) ** 2
            for tid, amp in self.tool_amplitudes.items()
        }

    def get_top_tools(self, k: int = 3) -> list[tuple[str, float]]:
        """Get top k tools by probability."""
        probs = self.get_probability_distribution()
        sorted_tools = sorted(
            probs.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_tools[:k]

    def get_entropy(self) -> float:
        """Compute von Neumann entropy of the state."""
        probs = self.get_probability_distribution()
        # S = -Σ p_i * log(p_i)
        entropy = 0.0
        for p in probs.values():
            if p > 1e-10:  # Avoid log(0)
                entropy -= p * np.log2(p)
        return entropy

    def get_purity(self) -> float:
        """Compute purity Tr(ρ²) of the state."""
        probs = self.get_probability_distribution()
        return sum(p ** 2 for p in probs.values())

    def is_pure(self, threshold: float = 0.99) -> bool:
        """Check if state is pure (purity ≈ 1)."""
        return self.get_purity() > threshold

    def is_maximally_entangled(self, threshold: float = 0.9) -> bool:
        """Check if state has maximum entropy (maximally mixed)."""
        n = len(self.tool_amplitudes)
        max_entropy = np.log2(n)
        current_entropy = self.get_entropy()
        return current_entropy > max_entropy * threshold


@dataclass
class QuantumPhase5State:
    """Phase 5-specific quantum state components for integration with FullAgentState."""

    quantum_amplitudes: dict[str, complex]
    entanglement_matrix: dict[str, dict]
    temperature: float
    amplification_iterations: int = 0
    tunneling_solutions: list[dict] = field(default_factory=list)
    quantum_metrics: dict[str, float] = field(default_factory=dict)
    annealing_schedule: str = "exponential"
    measurement_type: str = QuantumMeasurementType.PROBABILISTIC.value

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "quantum_amplitudes": {
                k: {"real": v.real, "imag": v.imag}
                for k, v in self.quantum_amplitudes.items()
            },
            "entanglement_matrix": self.entanglement_matrix,
            "temperature": self.temperature,
            "amplification_iterations": self.amplification_iterations,
            "tunneling_solutions": self.tunneling_solutions,
            "quantum_metrics": self.quantum_metrics,
        }


class QuantumEnergyEvaluator:
    """Evaluates 'energy' (quality metric) of tool combinations."""

    def __init__(self, registry):
        self.registry = registry

    def evaluate(self, tool_ids: list[str]) -> float:
        """
        Compute energy (negative = better).

        Combines:
        - Coverage: tools address task aspects
        - Efficiency: minimal tool count
        - Chainability: tools can run in sequence
        - Safety: no violations
        """
        if not tool_ids:
            return float("inf")

        energy = 0.0

        # Objective 1: Coverage (higher is better, so negative energy)
        coverage = self._compute_coverage(tool_ids)
        energy -= coverage * 0.4

        # Objective 2: Efficiency (prefer fewer tools)
        energy += len(tool_ids) * 0.1

        # Objective 3: Chainability (prefer connectable tools)
        chainable_score = self._compute_chainability(tool_ids)
        energy -= chainable_score * 0.3

        # Objective 4: Diversity (prefer diverse capabilities)
        diversity = self._compute_diversity(tool_ids)
        energy -= diversity * 0.2

        return energy

    def _compute_coverage(self, tool_ids: list[str]) -> float:
        """Measure how comprehensively tools cover task needs."""
        all_capabilities = set()
        for tool_id in tool_ids:
            tool_lookup = self.registry.get(tool_id)
            if tool_lookup:
                schema, _ = tool_lookup
                all_capabilities.update(schema.capabilities)

        return len(all_capabilities) / max(1, len(all_capabilities))

    def _compute_chainability(self, tool_ids: list[str]) -> float:
        """Measure how well tools can be chained together."""
        if len(tool_ids) < 2:
            return 0.5

        compatible_pairs = 0
        total_pairs = 0

        for i, tool_a_id in enumerate(tool_ids):
            tool_a = self.registry.get(tool_a_id)
            if not tool_a:
                continue
            schema_a, _ = tool_a
            return_type_a = schema_a.return_type

            for tool_b_id in tool_ids[i + 1 :]:
                tool_b = self.registry.get(tool_b_id)
                if not tool_b:
                    continue
                schema_b, _ = tool_b

                total_pairs += 1

                # Check if A's output matches B's input
                param_types_b = {p.type for p in schema_b.parameters}
                if return_type_a in param_types_b:
                    compatible_pairs += 1

        if total_pairs == 0:
            return 0.5

        return compatible_pairs / total_pairs

    def _compute_diversity(self, tool_ids: list[str]) -> float:
        """Measure diversity of tool categories."""
        categories = set()
        for tool_id in tool_ids:
            tool_lookup = self.registry.get(tool_id)
            if tool_lookup:
                schema, _ = tool_lookup
                categories.add(schema.category)

        return len(categories) / len(tool_ids)


def normalize_amplitudes(amplitudes: dict[str, complex]) -> dict[str, complex]:
    """Normalize amplitudes to ensure Σ|α_i|² = 1."""
    total_prob = sum(abs(amp) ** 2 for amp in amplitudes.values())
    if total_prob == 0:
        # Equal superposition fallback
        n = len(amplitudes)
        return {tid: 1.0 / np.sqrt(n) for tid in amplitudes.keys()}
    return {
        tid: amp / np.sqrt(total_prob)
        for tid, amp in amplitudes.items()
    }


def compute_phase_shift(
    reasoning_score: float,
    attention_score: float,
    category_relevance: float = 1.0
) -> float:
    """
    Compute phase angle for amplitude based on reasoning and consciousness.

    Returns phase in radians [0, 2π].
    """
    # Combine scoring components
    reasoning_phase = reasoning_score * 0.6
    attention_phase = attention_score * 0.3
    category_phase = category_relevance * 0.1

    total_phase = reasoning_phase + attention_phase + category_phase
    return total_phase * np.pi
