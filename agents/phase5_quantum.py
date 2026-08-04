"""Phase 5: Quantum-Inspired Reasoning & Optimization."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState
from quantum.superposition import SuperpositionEngine
from quantum.entanglement import EntanglementMatrix
from quantum.tunneling import TunnelingExplorer
from quantum.amplitude_amplification import AmplitudeAmplifier
from quantum.annealing import QuantumAnnealingSchedule
from quantum.metrics import compute_quantum_metrics, get_quantum_summary
from tools.schema import ToolRegistry


LLMFn = Callable[[str], str]


def make_quantum_optimization_node(llm: LLMFn, registry: ToolRegistry):
    """
    Create Phase 5 quantum optimization node.

    Applies quantum-inspired algorithms to enhance tool selection from Phase 4.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 5: Quantum-Inspired Tool Optimization.

        Takes Phase 4 tool selection and optimizes using:
        1. Superposition - Create probability distribution
        2. Entanglement - Track parameter coupling
        3. Tunneling - Explore alternatives
        4. Amplitude Amplification - Boost promising tools
        5. Annealing - Converge to optimal solution
        """
        if not state.get("selected_tools"):
            # No tools selected in Phase 4, skip quantum optimization
            return state

        # Get available tool IDs (list_all returns schemas)
        tool_schemas = registry.list_all()
        available_tools = [schema.id for schema in tool_schemas]
        current_tools = state.get("selected_tools", [])

        if not available_tools:
            return state

        # Initialize quantum components
        superposition = SuperpositionEngine(registry)
        entanglement = EntanglementMatrix(registry)
        tunneling = TunnelingExplorer(registry)
        amplifier = AmplitudeAmplifier(registry)
        annealer = QuantumAnnealingSchedule(registry)

        # Step 1: Create initial superposition
        reasoning = {
            "reasoning_type": state.get("reasoning_type", "logical"),
            "relevant_categories": state.get("relevant_categories", []),
            "required_capabilities": state.get("required_capabilities", [])
        }
        consciousness_state = {
            "attention_focus": state.get("attention_focus", []),
            "metacognitive_notes": state.get("metacognitive_notes", "")
        }

        quantum_state = superposition.create_initial_superposition(
            reasoning,
            consciousness_state,
            available_tools,
            initial_temperature=1.0
        )

        # Step 2: Apply entanglement coupling
        entanglement_matrix = entanglement.compute_entanglement_matrix(available_tools)
        quantum_state = entanglement.apply_entanglement_to_state(
            quantum_state, entanglement_matrix
        )

        # Step 3: Explore tunneling alternatives
        tunneling_solutions, quantum_state = tunneling.escape_local_optimum(
            current_tools,
            available_tools,
            quantum_state,
            escape_probability=0.3
        )

        # Step 4: Amplify tools matching reasoning/creativity
        creative_ideas = state.get("creative_ideas", [])
        if creative_ideas:
            # Mark tools that support creative ideas
            oracle = lambda tid: any(
                idea.lower() in tid.lower() or
                any(keyword.lower() in tid.lower() for keyword in idea.split())
                for idea in creative_ideas
            )
        else:
            # Default oracle: mark tools from current selection
            oracle = lambda tid: tid in current_tools

        quantum_state = amplifier.amplify_tools(
            quantum_state,
            oracle_fn=oracle,
            num_iterations=2
        )

        # Step 5: Anneal toward optimal solution
        quantum_state = annealer.apply_annealing_to_state(
            quantum_state,
            schedule_type="exponential",
            total_iterations=10
        )

        # Measure: collapse superposition to classical tool selection
        optimized_tools = superposition.collapse_to_measurement(
            quantum_state,
            measurement_type="probabilistic",
            seed=42
        )

        # Compute metrics
        quantum_metrics = compute_quantum_metrics(quantum_state)

        # Update state with Phase 5 results
        state.update({
            "quantum_state_created": True,
            "quantum_amplitudes": dict(quantum_state.tool_amplitudes),
            "quantum_entanglement_matrix": entanglement_matrix,
            "quantum_tunneling_solutions": tunneling_solutions,
            "quantum_metrics": quantum_metrics,
            "quantum_optimized_tools": optimized_tools,
            "quantum_entropy": quantum_metrics.get("entropy", 0.0),
            "quantum_purity": quantum_metrics.get("purity", 0.0),
        })

        return state

    return process


def make_phase5_summary_node(llm: LLMFn):
    """
    Create Phase 5 summary node.

    Generates human-readable summary of quantum optimization.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate summary of Phase 5 results."""
        if not state.get("quantum_state_created"):
            return state

        summary_lines = [
            "=== Phase 5: Quantum-Inspired Optimization ===",
            f"Original tool selection: {state.get('selected_tools', [])}",
            f"Quantum-optimized tools: {state.get('quantum_optimized_tools', [])}",
            f"Superposition entropy: {state.get('quantum_entropy', 0.0):.4f}",
            f"State purity: {state.get('quantum_purity', 0.0):.4f}",
            f"Tunneling alternatives found: {len(state.get('quantum_tunneling_solutions', []))}",
        ]

        phase5_summary = "\n".join(summary_lines)

        state.update({
            "phase5_summary": phase5_summary,
        })

        return state

    return process
