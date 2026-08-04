"""Quantum Superposition Engine - Initialize tool probability distributions."""

from __future__ import annotations

from typing import Callable, Optional
import numpy as np
from quantum.principles import (
    QuantumState,
    normalize_amplitudes,
    compute_phase_shift,
)


class SuperpositionEngine:
    """Initialize and manage quantum superposition of tools."""

    def __init__(self, registry, llm: Optional[Callable] = None):
        self.registry = registry
        self.llm = llm

    def create_initial_superposition(
        self,
        reasoning: dict,
        consciousness_state: dict,
        available_tools: list,
        initial_temperature: float = 1.0,
    ) -> QuantumState:
        """
        Create initial quantum superposition of tools.

        Start with equal superposition, then weight by reasoning + consciousness.
        """
        N = len(available_tools)
        if N == 0:
            return QuantumState(tool_amplitudes={})

        amplitudes = {}

        for tool_id in available_tools:
            # Base amplitude: equal superposition
            base_amplitude = 1.0 / np.sqrt(N)

            # Compute reasoning score for this tool
            reasoning_score = self._analyze_tool_fit(
                tool_id, reasoning
            )

            # Compute attention fit
            attention_score = self._analyze_attention_fit(
                tool_id, consciousness_state
            )

            # Category relevance
            category_relevance = self._compute_category_relevance(
                tool_id, reasoning
            )

            # Combine into phase shift
            phase = compute_phase_shift(
                reasoning_score,
                attention_score,
                category_relevance
            )

            # Create complex amplitude: |ψ⟩ = (1/√N) * e^(i*phase)
            amplitude = base_amplitude * np.exp(1j * phase)
            amplitudes[tool_id] = amplitude

        # Normalize to ensure probability conservation
        amplitudes = normalize_amplitudes(amplitudes)

        return QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings={},
            temperature=initial_temperature,
            iteration=0,
        )

    def _analyze_tool_fit(self, tool_id, reasoning: dict) -> float:
        """
        Score how well tool matches the reasoning.

        Returns value in [0, 1] based on reasoning components.
        """
        score = 0.0

        # Lookup tool in registry
        tool_lookup = self.registry.get(tool_id)
        if not tool_lookup:
            return 0.0

        schema, _ = tool_lookup

        # Check reasoning type compatibility
        reasoning_type = reasoning.get("reasoning_type", "")
        if reasoning_type in ["causal", "multi-modal"]:
            if "analysis" in schema.capabilities or "reasoning" in schema.capabilities:
                score += 0.3

        # Check if tool handles reasoning outputs
        if "probabilistic" in schema.capabilities:
            score += 0.2

        # Check if tool is in relevant category
        reasoning_categories = reasoning.get("relevant_categories", [])
        if schema.category in reasoning_categories:
            score += 0.25

        # Check capabilities match
        reasoning_capabilities = reasoning.get("required_capabilities", [])
        matching = sum(
            1 for cap in reasoning_capabilities
            if cap in schema.capabilities
        )
        score += (matching / max(len(reasoning_capabilities), 1)) * 0.25

        return min(score, 1.0)

    def _analyze_attention_fit(
        self,
        tool_id,
        consciousness_state: dict
    ) -> float:
        """
        Score how well tool matches consciousness attention focus.

        Returns value in [0, 1].
        """
        attention_focus = consciousness_state.get("attention_focus", [])
        if not attention_focus:
            return 0.5  # Default if no attention specified

        # Lookup tool in registry
        tool_lookup = self.registry.get(tool_id)
        if not tool_lookup:
            return 0.0

        schema, _ = tool_lookup

        # Check if tool addresses attention focus areas
        matching = sum(
            1 for focus in attention_focus
            if focus.lower() in schema.description.lower() or
            any(focus.lower() in cap.lower() for cap in schema.capabilities)
        )

        return matching / max(len(attention_focus), 1)

    def _compute_category_relevance(
        self,
        tool_id,
        reasoning: dict
    ) -> float:
        """
        Score category relevance to reasoning task.

        Returns value in [0, 1].
        """
        # Lookup tool in registry
        tool_lookup = self.registry.get(tool_id)
        if not tool_lookup:
            return 0.0

        schema, _ = tool_lookup

        reasoning_type = reasoning.get("reasoning_type", "")

        # Map reasoning types to relevant tool categories
        type_to_categories = {
            "causal": ["logic", "reasoning"],
            "logical": ["logic", "data"],
            "probabilistic": ["math", "data"],
            "common_sense": ["text", "logic"],
            "multi-modal": ["text", "math", "logic", "data"],
        }

        relevant_categories = type_to_categories.get(
            reasoning_type,
            []
        )

        if schema.category in relevant_categories:
            return 1.0
        elif schema.category in ["custom", "data"]:
            return 0.7
        else:
            return 0.3

    def apply_consciousness_modulation(
        self,
        quantum_state: QuantumState,
        consciousness_state: dict
    ) -> QuantumState:
        """
        Modulate amplitudes based on consciousness constraints.

        Updates existing superposition with consciousness awareness.
        """
        amplitudes = quantum_state.tool_amplitudes.copy()

        attention_focus = consciousness_state.get("attention_focus", [])
        metacognition = consciousness_state.get("metacognitive_notes", "")

        # Extract uncertainty from metacognition
        uncertainty_markers = ["uncertain", "limited", "weak", "poor"]
        has_uncertainty = any(
            marker in metacognition.lower()
            for marker in uncertainty_markers
        )

        # Modulate amplitudes
        for tool_id, amp in amplitudes.items():
            tool_lookup = self.registry.get(tool_id)
            if not tool_lookup:
                continue

            schema, _ = tool_lookup

            # Amplify if tool addresses attention focus
            if any(
                focus.lower() in schema.description.lower()
                for focus in attention_focus
            ):
                amplitudes[tool_id] = amp * 1.2

            # Suppress if there's metacognitive uncertainty
            if has_uncertainty and schema.requires_network:
                amplitudes[tool_id] = amp * 0.8

        # Renormalize
        amplitudes = normalize_amplitudes(amplitudes)

        return QuantumState(
            tool_amplitudes=amplitudes,
            parameter_couplings=quantum_state.parameter_couplings,
            temperature=quantum_state.temperature,
            iteration=quantum_state.iteration,
            history=quantum_state.history,
        )

    def compute_superposition_entropy(
        self,
        quantum_state: QuantumState
    ) -> float:
        """
        Compute von Neumann entropy of the superposition.

        High entropy = many tools equally probable (exploration)
        Low entropy = few tools likely (exploitation)
        """
        return quantum_state.get_entropy()

    def get_dominant_tools(
        self,
        quantum_state: QuantumState,
        k: int = 3
    ) -> list[tuple[str, float]]:
        """Get k most probable tools and their probabilities."""
        return quantum_state.get_top_tools(k)

    def collapse_to_measurement(
        self,
        quantum_state: QuantumState,
        measurement_type: str = "probabilistic",
        seed: Optional[int] = None
    ) -> list[str]:
        """
        Collapse superposition to classical tool selection.

        measurement_type:
        - "probabilistic": Sample per |ψ|² distribution
        - "deterministic": Always highest probability
        - "threshold": All above-average probability
        - "weighted": Weighted random selection
        """
        if seed is not None:
            np.random.seed(seed)

        amplitudes = quantum_state.tool_amplitudes
        tool_ids = list(amplitudes.keys())
        probabilities = [abs(amplitudes[tid]) ** 2 for tid in tool_ids]

        # Ensure probabilities sum to 1
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]

        if measurement_type == "probabilistic":
            # Sample up to 3 tools according to probabilities
            num_tools = min(3, len(tool_ids))
            selected = np.random.choice(
                tool_ids,
                size=num_tools,
                replace=False,
                p=probabilities
            )
            return sorted(selected)

        elif measurement_type == "deterministic":
            # Always choose highest probability tools
            sorted_tools = sorted(
                zip(tool_ids, probabilities),
                key=lambda x: x[1],
                reverse=True
            )
            return [tid for tid, _ in sorted_tools[:3]]

        elif measurement_type == "threshold":
            # Choose all tools above average probability
            avg_prob = np.mean(probabilities)
            selected = [
                tid for tid, prob in zip(tool_ids, probabilities)
                if prob > avg_prob
            ]
            return selected if selected else [tool_ids[0]]

        elif measurement_type == "weighted":
            # Weighted random selection
            weights = np.array(probabilities) ** 0.5  # Soften probabilities
            weights = weights / weights.sum()
            num_tools = max(1, min(3, int(np.sum(weights > 0.1))))
            selected = np.random.choice(
                tool_ids,
                size=num_tools,
                replace=False,
                p=probabilities
            )
            return sorted(selected)

        else:
            return [tool_ids[0]] if tool_ids else []
