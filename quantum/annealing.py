"""Quantum Annealing Schedule - Temperature-based convergence strategy."""

from __future__ import annotations

from typing import Literal
import numpy as np
from quantum.principles import QuantumState, QuantumEnergyEvaluator


class QuantumAnnealingSchedule:
    """Temperature schedule for quantum annealing (Algorithm 2.5)."""

    def __init__(self, registry):
        """
        Initialize annealing schedule.

        registry: Tool registry for schema lookups
        """
        self.registry = registry
        self.energy_evaluator = QuantumEnergyEvaluator(registry)

    def compute_temperature(
        self,
        iteration: int,
        schedule_type: Literal["exponential", "linear", "logarithmic", "adaptive"] = "exponential",
        initial_temperature: float = 1.0,
        final_temperature: float = 0.01,
        total_iterations: int = 100
    ) -> float:
        """
        Compute temperature for given iteration.

        schedule_type:
        - "exponential": T(t) = T_0 * exp(-αt)
        - "linear": T(t) = T_0 * (1 - t/T_max)
        - "logarithmic": T(t) = T_0 / log(t + 2)
        - "adaptive": Changes based on energy progress
        """
        if schedule_type == "exponential":
            alpha = -np.log(final_temperature / initial_temperature) / total_iterations
            return initial_temperature * np.exp(-alpha * iteration)

        elif schedule_type == "linear":
            return initial_temperature * (
                1 - iteration / max(total_iterations, 1)
            )

        elif schedule_type == "logarithmic":
            return initial_temperature / np.log(iteration + 2)

        elif schedule_type == "adaptive":
            # Adaptive: decay slower than exponential initially, faster later
            t_normalized = iteration / max(total_iterations, 1)
            exponent = t_normalized ** 1.5  # Cubic growth of exponent
            return initial_temperature * np.exp(-3 * exponent)

        else:
            return initial_temperature

    def apply_annealing_to_state(
        self,
        quantum_state: QuantumState,
        schedule_type: str = "exponential",
        total_iterations: int = 100
    ) -> QuantumState:
        """
        Update state with annealing temperature schedule.

        Modifies temperature based on iteration count.
        """
        current_iter = quantum_state.iteration
        new_temperature = self.compute_temperature(
            current_iter,
            schedule_type=schedule_type,
            initial_temperature=quantum_state.temperature,
            total_iterations=total_iterations
        )

        return QuantumState(
            tool_amplitudes=quantum_state.tool_amplitudes,
            parameter_couplings=quantum_state.parameter_couplings,
            temperature=new_temperature,
            iteration=current_iter,
            history=quantum_state.history,
        )

    def metropolis_accept(
        self,
        current_energy: float,
        proposed_energy: float,
        temperature: float
    ) -> bool:
        """
        Metropolis acceptance criterion for annealing step.

        Returns whether to accept new configuration.
        """
        if proposed_energy < current_energy:
            return True  # Accept better solution

        # Accept worse solution with probability exp(-ΔE/T)
        energy_diff = proposed_energy - current_energy
        acceptance_prob = np.exp(-energy_diff / max(temperature, 0.01))
        return np.random.random() < acceptance_prob

    def anneal_superposition(
        self,
        quantum_state: QuantumState,
        target_configuration: list[str],
        schedule_type: str = "exponential",
        num_steps: int = 50
    ) -> QuantumState:
        """
        Anneal superposition toward target configuration.

        Gradually increases probability of target tools.
        """
        state = quantum_state
        target_set = set(target_configuration)

        for step in range(num_steps):
            temperature = self.compute_temperature(
                step,
                schedule_type=schedule_type,
                initial_temperature=quantum_state.temperature,
                total_iterations=num_steps
            )

            # Modify amplitudes toward target
            amplitudes = state.tool_amplitudes.copy()

            for tool_id in amplitudes.keys():
                if tool_id in target_set:
                    # Boost target tools
                    boost = 1.0 + (1 - step / num_steps) * 0.5
                    amplitudes[tool_id] *= boost
                else:
                    # Suppress non-target tools based on temperature
                    suppression = np.exp(-temperature * 2)
                    amplitudes[tool_id] *= suppression

            # Renormalize
            total_prob = sum(abs(amp) ** 2 for amp in amplitudes.values())
            if total_prob > 0:
                amplitudes = {
                    tid: amp / np.sqrt(total_prob)
                    for tid, amp in amplitudes.items()
                }

            state = QuantumState(
                tool_amplitudes=amplitudes,
                parameter_couplings=state.parameter_couplings,
                temperature=temperature,
                iteration=state.iteration + 1,
                history=state.history,
            )

        return state

    def get_convergence_metric(
        self,
        quantum_state: QuantumState,
        target_configuration: list[str]
    ) -> float:
        """
        Compute convergence of state toward target configuration.

        Returns value in [0, 1] where 1 = fully converged to target.
        """
        probs = quantum_state.get_probability_distribution()
        target_prob = sum(probs.get(tid, 0) for tid in target_configuration)
        return float(target_prob)

    def optimize_with_annealing(
        self,
        available_tools: list[str],
        oracle_fn: callable,
        schedule_type: str = "exponential",
        max_iterations: int = 100
    ) -> tuple[list[str], QuantumState, list[dict]]:
        """
        Run full annealing optimization.

        Returns (best_configuration, final_state, history).
        """
        from quantum.superposition import SuperpositionEngine

        engine = SuperpositionEngine(self.registry)

        # Initialize with uniform superposition
        initial_state = engine.create_initial_superposition(
            reasoning={},
            consciousness_state={},
            available_tools=available_tools,
            initial_temperature=1.0
        )

        state = initial_state
        best_config = available_tools[:3]
        best_energy = self.energy_evaluator.evaluate(best_config)
        history = []

        for iteration in range(max_iterations):
            # Update temperature
            temperature = self.compute_temperature(
                iteration,
                schedule_type=schedule_type,
                initial_temperature=1.0,
                final_iterations=max_iterations
            )

            # Sample candidate configuration
            probs = state.get_probability_distribution()
            top_tools = sorted(
                probs.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            candidate = [tid for tid, _ in top_tools]

            # Evaluate candidate
            candidate_energy = self.energy_evaluator.evaluate(candidate)

            # Metropolis acceptance
            if self.metropolis_accept(best_energy, candidate_energy, temperature):
                best_config = candidate
                best_energy = candidate_energy

            # Update state temperature
            state = self.apply_annealing_to_state(
                state,
                schedule_type=schedule_type,
                total_iterations=max_iterations
            )

            history.append({
                "iteration": iteration,
                "temperature": temperature,
                "best_energy": best_energy,
                "best_config": best_config,
                "purity": state.get_purity(),
                "entropy": state.get_entropy(),
            })

            # Early stopping if converged
            if state.get_purity() > 0.95:
                break

        return best_config, state, history

    def get_schedule_trajectory(
        self,
        schedule_type: str = "exponential",
        initial_temperature: float = 1.0,
        final_temperature: float = 0.01,
        num_points: int = 50
    ) -> list[tuple[int, float]]:
        """
        Get temperature trajectory for plotting.

        Returns list of (iteration, temperature) points.
        """
        trajectory = []
        for i in range(num_points):
            temp = self.compute_temperature(
                i,
                schedule_type=schedule_type,
                initial_temperature=initial_temperature,
                final_temperature=final_temperature,
                total_iterations=num_points
            )
            trajectory.append((i, temp))

        return trajectory

    def compare_schedules(
        self,
        num_points: int = 50
    ) -> dict[str, list[tuple[int, float]]]:
        """
        Get trajectories for all schedule types.

        Useful for visualization and comparison.
        """
        schedules = {
            "exponential": self.get_schedule_trajectory(
                "exponential", num_points=num_points
            ),
            "linear": self.get_schedule_trajectory(
                "linear", num_points=num_points
            ),
            "logarithmic": self.get_schedule_trajectory(
                "logarithmic", num_points=num_points
            ),
            "adaptive": self.get_schedule_trajectory(
                "adaptive", num_points=num_points
            ),
        }
        return schedules
