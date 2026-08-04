"""Quantum Tunneling - Escape local optima by exploring alternative tool configurations."""

from __future__ import annotations

from typing import Optional
import numpy as np
from quantum.principles import QuantumState, QuantumEnergyEvaluator


class TunnelingExplorer:
    """Explore energy landscape to escape local optima (Algorithm 2.3)."""

    def __init__(self, registry):
        """
        Initialize tunneling explorer.

        registry: Tool registry for schema lookups
        """
        self.registry = registry
        self.energy_evaluator = QuantumEnergyEvaluator(registry)

    def find_tunneling_paths(
        self,
        current_tools: list[str],
        available_tools: list[str],
        energy_limit: float = 5.0,
        max_substitutions: int = 2
    ) -> list[dict]:
        """
        Find alternative tool configurations by "tunneling" through energy barriers.

        Generates nearby configurations by substituting 1-2 tools, keeping energy
        reasonable.

        Returns list of {config, energy, jump_distance, explanation}.
        """
        solutions = []
        current_energy = self.energy_evaluator.evaluate(current_tools)
        candidate_pool = set(available_tools) - set(current_tools)

        if not candidate_pool:
            return solutions

        # Single substitutions
        for removed_tool in current_tools:
            for added_tool in candidate_pool:
                alternative = [
                    t for t in current_tools if t != removed_tool
                ] + [added_tool]
                alt_energy = self.energy_evaluator.evaluate(alternative)

                # Only accept if energy increase is reasonable (tunneling through barrier)
                if alt_energy < current_energy + energy_limit:
                    distance = len(
                        set(current_tools) ^ set(alternative)
                    )
                    solutions.append({
                        "config": alternative,
                        "energy": alt_energy,
                        "jump_distance": distance,
                        "explanation": f"Replaced {removed_tool} with {added_tool}"
                    })

        # Double substitutions (if pool large enough)
        if len(candidate_pool) >= 2 and max_substitutions >= 2:
            candidate_list = list(candidate_pool)
            for i, added_a in enumerate(candidate_list):
                for added_b in candidate_list[i + 1:]:
                    for removed_a in current_tools:
                        remaining = [
                            t for t in current_tools if t != removed_a
                        ]
                        for removed_b in remaining:
                            alternative = [
                                t for t in remaining if t != removed_b
                            ] + [added_a, added_b]
                            alt_energy = self.energy_evaluator.evaluate(
                                alternative
                            )

                            if alt_energy < current_energy + energy_limit:
                                distance = len(
                                    set(current_tools) ^ set(alternative)
                                )
                                solutions.append({
                                    "config": alternative,
                                    "energy": alt_energy,
                                    "jump_distance": distance,
                                    "explanation": f"Replaced {removed_a}, {removed_b} with {added_a}, {added_b}"
                                })

        # Sort by energy (best first)
        solutions.sort(key=lambda x: x["energy"])
        return solutions[:10]  # Return top 10 solutions

    def apply_tunneling_to_state(
        self,
        quantum_state: QuantumState,
        tunneling_solutions: list[dict],
        tunneling_temperature: float = 1.0
    ) -> QuantumState:
        """
        Incorporate tunneling solutions into superposition state.

        Adds amplitude contribution from alternative configurations.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()

        for solution in tunneling_solutions:
            alt_config = solution["config"]
            energy = solution["energy"]

            # Boltzmann factor for this configuration
            probability = np.exp(-energy / max(tunneling_temperature, 0.1))

            # Add amplitude for each tool in the alternative configuration
            for tool_id in alt_config:
                if tool_id not in amplitudes:
                    # New tool discovered via tunneling
                    amplitudes[tool_id] = (
                        np.sqrt(probability) / len(alt_config)
                    )
                else:
                    # Boost amplitude via tunneling contribution
                    amplitudes[tool_id] += (
                        np.sqrt(probability) / len(alt_config)
                    )

        # Renormalize
        total_prob = sum(abs(amp) ** 2 for amp in amplitudes.values())
        if total_prob > 0:
            amplitudes = {
                tid: amp / np.sqrt(total_prob)
                for tid, amp in amplitudes.items()
            }

        return QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings=quantum_state.parameter_couplings,
            temperature=quantum_state.temperature,
            iteration=quantum_state.iteration + 1,
            history=quantum_state.history,
        )

    def escape_local_optimum(
        self,
        current_tools: list[str],
        available_tools: list[str],
        quantum_state: QuantumState,
        escape_probability: float = 0.3
    ) -> tuple[list[dict], QuantumState]:
        """
        Attempt to escape current local optimum via tunneling.

        Returns (tunneling_solutions, updated_state).
        """
        current_energy = self.energy_evaluator.evaluate(current_tools)

        # Find alternative configurations
        tunneling_solutions = self.find_tunneling_paths(
            current_tools,
            available_tools,
            energy_limit=current_energy * 0.5
        )

        if not tunneling_solutions:
            return [], quantum_state

        # Accept escape with probability
        if np.random.random() < escape_probability:
            # Apply tunneling to state
            new_state = self.apply_tunneling_to_state(
                quantum_state,
                tunneling_solutions,
                tunneling_temperature=quantum_state.temperature
            )
            return tunneling_solutions, new_state

        return tunneling_solutions, quantum_state

    def compute_barrier_height(
        self,
        source_tools: list[str],
        target_tools: list[str]
    ) -> float:
        """
        Compute energy barrier height between two configurations.

        Returns energy difference (positive = uphill tunneling).
        """
        source_energy = self.energy_evaluator.evaluate(source_tools)
        target_energy = self.energy_evaluator.evaluate(target_tools)

        return max(0.0, target_energy - source_energy)

    def compute_tunneling_probability(
        self,
        barrier_height: float,
        distance: int,
        temperature: float = 1.0
    ) -> float:
        """
        Compute quantum tunneling probability through barrier.

        Uses simplified Boltzmann factor: P ∝ exp(-E/T).
        distance: Hamming distance between configurations.
        """
        if temperature < 0.01:
            return 0.0

        # Adjust barrier by distance (more substitutions = harder tunneling)
        adjusted_barrier = barrier_height + distance * 0.2

        # Boltzmann tunneling probability
        prob = np.exp(-adjusted_barrier / temperature)
        return float(np.clip(prob, 0.0, 1.0))

    def get_tunneling_statistics(
        self,
        current_tools: list[str],
        available_tools: list[str]
    ) -> dict:
        """
        Compute statistics about tunneling landscape.

        Returns landscape analysis for current configuration.
        """
        tunneling_solutions = self.find_tunneling_paths(
            current_tools,
            available_tools,
            energy_limit=10.0,
            max_substitutions=2
        )

        if not tunneling_solutions:
            return {
                "escape_routes": 0,
                "min_barrier": float("inf"),
                "max_barrier": 0.0,
                "avg_barrier": 0.0,
                "landscape_complexity": 0.0,
            }

        current_energy = self.energy_evaluator.evaluate(current_tools)
        barriers = [
            s["energy"] - current_energy
            for s in tunneling_solutions
        ]

        return {
            "escape_routes": len(tunneling_solutions),
            "min_barrier": float(np.min(barriers)) if barriers else 0.0,
            "max_barrier": float(np.max(barriers)) if barriers else 0.0,
            "avg_barrier": float(np.mean(barriers)) if barriers else 0.0,
            "landscape_complexity": float(np.std(barriers)) if barriers else 0.0,
        }
