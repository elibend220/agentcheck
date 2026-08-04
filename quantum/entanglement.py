"""Quantum Entanglement Matrix - Parameter coupling and dependency tracking."""

from __future__ import annotations

from typing import Optional
import numpy as np
from quantum.principles import QuantumState


class EntanglementMatrix:
    """Track and manage parameter coupling between tools (Algorithm 2.2)."""

    def __init__(self, registry):
        """
        Initialize entanglement tracking.

        registry: Tool registry for schema lookups
        """
        self.registry = registry
        self._coupling_cache = {}

    def compute_entanglement_matrix(
        self,
        tool_ids: list[str]
    ) -> dict[str, dict[str, float]]:
        """
        Compute parameter coupling strength between all tool pairs.

        Returns matrix[tool_a_id][tool_b_id] = coupling_strength in [0, 1].
        """
        matrix = {}

        for tool_a_id in tool_ids:
            matrix[tool_a_id] = {}
            for tool_b_id in tool_ids:
                if tool_a_id == tool_b_id:
                    matrix[tool_a_id][tool_b_id] = 1.0
                else:
                    strength = self._compute_coupling_strength(
                        tool_a_id, tool_b_id
                    )
                    matrix[tool_a_id][tool_b_id] = strength

        return matrix

    def _compute_coupling_strength(
        self,
        tool_a_id: str,
        tool_b_id: str
    ) -> float:
        """
        Compute coupling strength between two tools.

        Returns value in [0, 1] based on parameter compatibility.
        """
        cache_key = (tool_a_id, tool_b_id)
        if cache_key in self._coupling_cache:
            return self._coupling_cache[cache_key]

        strength = 0.0

        tool_a = self.registry.get(tool_a_id)
        tool_b = self.registry.get(tool_b_id)

        if not tool_a or not tool_b:
            self._coupling_cache[cache_key] = 0.0
            return 0.0

        schema_a, _ = tool_a
        schema_b, _ = tool_b

        # Check output -> input type compatibility
        return_type_a = schema_a.return_type
        param_types_b = {p.type for p in schema_b.parameters}

        if return_type_a in param_types_b:
            strength += 0.5

        # Check capability overlap
        caps_a = set(schema_a.capabilities)
        caps_b = set(schema_b.capabilities)
        overlap = len(caps_a & caps_b)
        if overlap > 0:
            strength += overlap / max(len(caps_a), len(caps_b)) * 0.3

        # Check category compatibility
        if schema_a.category == schema_b.category:
            strength += 0.2

        strength = min(strength, 1.0)
        self._coupling_cache[cache_key] = strength
        return strength

    def apply_entanglement_to_state(
        self,
        quantum_state: QuantumState,
        entanglement_matrix: dict[str, dict[str, float]]
    ) -> QuantumState:
        """
        Modify amplitudes based on entanglement between tools.

        Coupled tools reinforce each other's amplitudes.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()
        tool_ids = list(amplitudes.keys())

        # For each tool, amplify based on coupled tools' probabilities
        for tool_id in tool_ids:
            if tool_id not in entanglement_matrix:
                continue

            coupling_boost = 0.0
            couplings = entanglement_matrix[tool_id]

            for coupled_id, strength in couplings.items():
                if coupled_id in amplitudes and coupled_id != tool_id:
                    coupled_prob = abs(amplitudes[coupled_id]) ** 2
                    coupling_boost += coupled_prob * strength

            # Boost amplitude by entanglement with high-probability tools
            boost_factor = 1.0 + coupling_boost * 0.1
            amplitudes[tool_id] *= boost_factor

        # Renormalize
        total_prob = sum(abs(amp) ** 2 for amp in amplitudes.values())
        if total_prob > 0:
            amplitudes = {
                tid: amp / np.sqrt(total_prob)
                for tid, amp in amplitudes.items()
            }

        return QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings=entanglement_matrix,
            temperature=quantum_state.temperature,
            iteration=quantum_state.iteration,
            history=quantum_state.history,
        )

    def get_coupled_tools(
        self,
        tool_id: str,
        entanglement_matrix: dict[str, dict[str, float]],
        threshold: float = 0.3
    ) -> list[tuple[str, float]]:
        """
        Get tools coupled to given tool above threshold.

        Returns list of (tool_id, coupling_strength) sorted by strength.
        """
        if tool_id not in entanglement_matrix:
            return []

        couplings = entanglement_matrix[tool_id]
        coupled = [
            (other_id, strength)
            for other_id, strength in couplings.items()
            if other_id != tool_id and strength >= threshold
        ]

        return sorted(coupled, key=lambda x: x[1], reverse=True)

    def propagate_parameter_update(
        self,
        quantum_state: QuantumState,
        source_tool_id: str,
        entanglement_matrix: dict[str, dict[str, float]],
        update_magnitude: float = 0.1
    ) -> QuantumState:
        """
        Propagate parameter update through entangled tools.

        When one tool's parameters update, coupled tools' amplitudes adjust.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()

        if source_tool_id not in entanglement_matrix:
            return quantum_state

        # Find coupled tools and adjust their amplitudes
        couplings = entanglement_matrix[source_tool_id]
        source_prob = abs(amplitudes[source_tool_id]) ** 2

        for coupled_id, strength in couplings.items():
            if coupled_id != source_tool_id and coupled_id in amplitudes:
                # Propagate update to coupled tool
                propagation = source_prob * strength * update_magnitude
                amplitudes[coupled_id] *= (1.0 + propagation)

        # Renormalize
        total_prob = sum(abs(amp) ** 2 for amp in amplitudes.values())
        if total_prob > 0:
            amplitudes = {
                tid: amp / np.sqrt(total_prob)
                for tid, amp in amplitudes.items()
            }

        return QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings=entanglement_matrix,
            temperature=quantum_state.temperature,
            iteration=quantum_state.iteration + 1,
            history=quantum_state.history,
        )

    def compute_entanglement_entropy(
        self,
        entanglement_matrix: dict[str, dict[str, float]]
    ) -> float:
        """
        Compute total entanglement entropy of the system.

        High entropy = many tools strongly coupled (exploration)
        Low entropy = few, weak couplings (exploitation)
        """
        if not entanglement_matrix:
            return 0.0

        entropies = []
        for tool_id, couplings in entanglement_matrix.items():
            # For each tool, compute entropy of its coupling distribution
            strengths = [
                s for other_id, s in couplings.items() if other_id != tool_id
            ]
            if strengths:
                # Normalize strengths to probability distribution
                total = sum(strengths)
                if total > 0:
                    probs = [s / total for s in strengths]
                    entropy = sum(
                        -p * np.log2(p + 1e-10) for p in probs
                    )
                    entropies.append(entropy)

        return np.mean(entropies) if entropies else 0.0

    def get_coupling_statistics(
        self,
        entanglement_matrix: dict[str, dict[str, float]]
    ) -> dict[str, float]:
        """
        Compute statistics about coupling distribution.

        Returns mean, max, min, median coupling strength.
        """
        all_couplings = []
        for tool_id, couplings in entanglement_matrix.items():
            for other_id, strength in couplings.items():
                if other_id != tool_id:
                    all_couplings.append(strength)

        if not all_couplings:
            return {
                "mean": 0.0,
                "max": 0.0,
                "min": 0.0,
                "median": 0.0,
                "std": 0.0,
            }

        return {
            "mean": float(np.mean(all_couplings)),
            "max": float(np.max(all_couplings)),
            "min": float(np.min(all_couplings)),
            "median": float(np.median(all_couplings)),
            "std": float(np.std(all_couplings)),
        }
