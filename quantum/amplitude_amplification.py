"""Quantum Amplitude Amplification - Grover-like algorithm to reinforce promising tools."""

from __future__ import annotations

from typing import Optional, Callable
import numpy as np
from quantum.principles import QuantumState, QuantumEnergyEvaluator


class AmplitudeAmplifier:
    """Amplitude amplification for tool selection (Algorithm 2.4)."""

    def __init__(self, registry):
        """
        Initialize amplitude amplifier.

        registry: Tool registry for schema lookups
        """
        self.registry = registry
        self.energy_evaluator = QuantumEnergyEvaluator(registry)

    def mark_promising_tools(
        self,
        quantum_state: QuantumState,
        oracle_fn: Optional[Callable] = None,
        threshold: float = 0.3
    ) -> tuple[list[str], QuantumState]:
        """
        Mark tools as "promising" using oracle function.

        oracle_fn: Function(tool_id) -> bool, marks tool as promising.
                  If None, uses probability-based marking (tools > threshold prob).

        Returns (marked_tools, marked_state) where marked_state has phase inversion
        for marked tools.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()
        tool_ids = list(amplitudes.keys())
        marked_tools = []

        if oracle_fn is None:
            # Default oracle: mark tools with probability > threshold
            probs = quantum_state.get_probability_distribution()
            marked_tools = [
                tid for tid, prob in probs.items() if prob >= threshold
            ]
        else:
            # Custom oracle
            marked_tools = [tid for tid in tool_ids if oracle_fn(tid)]

        # Invert phase of marked tools (Grover's trick)
        for tool_id in marked_tools:
            if tool_id in amplitudes:
                amplitudes[tool_id] *= -1

        return marked_tools, QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings=quantum_state.parameter_couplings,
            temperature=quantum_state.temperature,
            iteration=quantum_state.iteration,
            history=quantum_state.history,
        )

    def amplify_iteration(
        self,
        quantum_state: QuantumState,
        marked_tools: list[str]
    ) -> QuantumState:
        """
        Perform one iteration of amplitude amplification (Grover diffusion).

        Amplifies marked tools, suppresses unmarked tools.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()
        tool_ids = list(amplitudes.keys())

        if not tool_ids:
            return quantum_state

        # Compute mean amplitude
        mean_amp = (
            sum(amplitudes.values()) / len(tool_ids)
        )

        # Diffusion operator: amp_new = 2 * mean - amp_old
        for tool_id in tool_ids:
            # Amplify marked tools
            if tool_id in marked_tools:
                amplitudes[tool_id] = 2 * mean_amp - amplitudes[tool_id]
            # Suppress unmarked tools slightly
            else:
                amplitudes[tool_id] = amplitudes[tool_id] * 0.9

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

    def amplify_tools(
        self,
        quantum_state: QuantumState,
        oracle_fn: Optional[Callable] = None,
        num_iterations: int = 2,
        threshold: float = 0.3
    ) -> QuantumState:
        """
        Apply full amplitude amplification procedure.

        Performs multiple iterations of marking + diffusion.
        Returns state with amplified marked tools.
        """
        state = quantum_state

        # Mark promising tools
        marked_tools, state = self.mark_promising_tools(
            state, oracle_fn, threshold
        )

        if not marked_tools:
            return state

        # Iterative amplification
        optimal_iterations = min(
            num_iterations,
            self._compute_optimal_iterations(len(marked_tools), len(state.tool_amplitudes))
        )

        for _ in range(optimal_iterations):
            state = self.amplify_iteration(state, marked_tools)

        return state

    def _compute_optimal_iterations(
        self,
        marked_count: int,
        total_count: int
    ) -> int:
        """
        Compute optimal number of Grover iterations.

        For N items with M marked, optimal iterations ≈ π/4 * sqrt(N/M).
        """
        if marked_count == 0 or total_count == 0:
            return 1

        ratio = total_count / marked_count
        optimal = int(np.pi / 4 * np.sqrt(ratio))
        return max(1, min(optimal, total_count))

    def amplify_by_energy(
        self,
        quantum_state: QuantumState,
        tool_combinations: Optional[list[list[str]]] = None,
        temperature: float = 1.0
    ) -> QuantumState:
        """
        Amplify tools based on energy evaluation of combinations.

        tool_combinations: List of tool sets to evaluate. If None, uses top tools.
        """
        if not tool_combinations:
            # Generate combinations from top tools
            top_tools = quantum_state.get_top_tools(k=5)
            tool_combinations = [
                [tid for tid, _ in top_tools[:i + 1]]
                for i in range(len(top_tools))
            ]

        # Evaluate energy of each combination
        energies = [
            self.energy_evaluator.evaluate(combo)
            for combo in tool_combinations
        ]

        # Lower energy = higher "promise"
        min_energy = min(energies) if energies else 0
        oracle_fn = lambda tid: any(
            tid in combo for combo, energy in zip(tool_combinations, energies)
            if energy < min_energy + 1.0
        )

        return self.amplify_tools(
            quantum_state,
            oracle_fn=oracle_fn,
            num_iterations=3,
            threshold=0.2
        )

    def get_amplification_factor(
        self,
        quantum_state: QuantumState,
        marked_tools: list[str]
    ) -> float:
        """
        Compute current amplification factor for marked tools.

        Returns ratio of marked probability to mean probability.
        """
        if not marked_tools:
            return 1.0

        probs = quantum_state.get_probability_distribution()
        marked_probs = [probs[tid] for tid in marked_tools if tid in probs]

        if not marked_probs:
            return 1.0

        marked_avg = np.mean(marked_probs)
        all_avg = np.mean(list(probs.values()))

        return marked_avg / max(all_avg, 1e-10)

    def compute_amplification_steps(
        self,
        initial_state: QuantumState,
        oracle_fn: Callable,
        max_iterations: int = 10
    ) -> list[tuple[float, float, float]]:
        """
        Trace amplification over multiple iterations.

        Returns list of (iteration, amplification_factor, entropy).
        """
        state = initial_state
        marked_tools, state = self.mark_promising_tools(state, oracle_fn)

        results = []

        for i in range(max_iterations):
            amp_factor = self.get_amplification_factor(state, marked_tools)
            entropy = state.get_entropy()
            results.append((float(i), amp_factor, entropy))

            # Stop if already amplified enough
            if amp_factor > 3.0:
                break

            state = self.amplify_iteration(state, marked_tools)

        return results
