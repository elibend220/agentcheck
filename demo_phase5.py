"""
Phase 5 Demo: Quantum-Inspired Reasoning & Optimization

Demonstrates the full 5-phase AGI framework with quantum-inspired algorithms
for tool selection and optimization.
"""

from agents.state import FullAgentState
from quantum.principles import QuantumState, QuantumPhase5State
from quantum.superposition import SuperpositionEngine
from quantum.entanglement import EntanglementMatrix
from quantum.tunneling import TunnelingExplorer
from quantum.amplitude_amplification import AmplitudeAmplifier
from quantum.annealing import QuantumAnnealingSchedule
from quantum.metrics import compute_quantum_metrics, compare_phase4_vs_phase5, get_quantum_summary
from tools.builtin import create_builtin_registry


def demo_quantum_superposition():
    """Demo 1: Quantum Superposition Engine."""
    print("\n" + "="*70)
    print("DEMO 1: Quantum Superposition Engine (Algorithm 2.1)")
    print("="*70)

    registry = create_builtin_registry()
    engine = SuperpositionEngine(registry)

    # Simulated Phase 1-3 outputs
    reasoning = {
        "reasoning_type": "causal",
        "relevant_categories": ["math", "text"],
        "required_capabilities": ["analysis"]
    }
    consciousness_state = {
        "attention_focus": ["math", "addition"],
        "metacognitive_notes": "weak understanding of math"
    }
    available_tools = ["math.add", "math.multiply", "text.uppercase"]

    # Create superposition
    state = engine.create_initial_superposition(
        reasoning, consciousness_state, available_tools, initial_temperature=1.0
    )

    print(f"\nInitial superposition over {len(available_tools)} tools:")
    print(f"  Entropy: {state.get_entropy():.4f} (exploration level)")
    print(f"  Purity: {state.get_purity():.4f}")

    top_tools = state.get_top_tools(k=3)
    print("\nTop tools by probability:")
    for tool_id, prob in top_tools:
        print(f"  {tool_id}: {prob:.4f}")

    # Apply consciousness modulation
    modulated = engine.apply_consciousness_modulation(state, consciousness_state)
    print("\nAfter consciousness modulation:")
    print(f"  Entropy: {modulated.get_entropy():.4f}")

    # Measurement
    selected = engine.collapse_to_measurement(state, measurement_type="probabilistic", seed=42)
    print(f"\nMeasurement (collapse to classical): {selected}")

    return state


def demo_quantum_entanglement():
    """Demo 2: Quantum Entanglement Matrix."""
    print("\n" + "="*70)
    print("DEMO 2: Quantum Entanglement Matrix (Algorithm 2.2)")
    print("="*70)

    registry = create_builtin_registry()
    entanglement = EntanglementMatrix(registry)

    tool_ids = ["math.add", "math.multiply", "text.uppercase"]

    # Compute entanglement
    matrix = entanglement.compute_entanglement_matrix(tool_ids)

    print(f"\nEntanglement coupling matrix ({len(tool_ids)}x{len(tool_ids)}):")
    print("     ", "  ".join(f"{tid[:8]:8}" for tid in tool_ids))
    for tool_a in tool_ids:
        row = []
        for tool_b in tool_ids:
            row.append(f"{matrix[tool_a][tool_b]:.3f}")
        print(f"{tool_a[:8]:8}", "  ".join(row))

    stats = entanglement.get_coupling_statistics(matrix)
    print(f"\nCoupling statistics:")
    print(f"  Mean: {stats['mean']:.4f}")
    print(f"  Max: {stats['max']:.4f}")
    print(f"  Entropy: {entanglement.compute_entanglement_entropy(matrix):.4f}")


def demo_quantum_tunneling():
    """Demo 3: Quantum Tunneling Explorer."""
    print("\n" + "="*70)
    print("DEMO 3: Quantum Tunneling Explorer (Algorithm 2.3)")
    print("="*70)

    registry = create_builtin_registry()
    explorer = TunnelingExplorer(registry)

    current_tools = ["math.add", "text.uppercase"]
    available_tools = ["math.add", "math.multiply", "text.uppercase", "text.split"]

    print(f"\nCurrent tool configuration: {current_tools}")
    print(f"Available alternative tools: {available_tools}")

    # Find tunneling paths
    solutions = explorer.find_tunneling_paths(
        current_tools, available_tools, energy_limit=5.0, max_substitutions=2
    )

    print(f"\nFound {len(solutions)} alternative configurations:")
    for i, sol in enumerate(solutions[:3]):
        print(f"\n  Alternative {i+1}:")
        print(f"    Config: {sol['config']}")
        print(f"    Energy: {sol['energy']:.4f}")
        print(f"    Explanation: {sol['explanation']}")


def demo_quantum_amplification():
    """Demo 4: Quantum Amplitude Amplification."""
    print("\n" + "="*70)
    print("DEMO 4: Quantum Amplitude Amplification (Algorithm 2.4)")
    print("="*70)

    registry = create_builtin_registry()
    amplifier = AmplitudeAmplifier(registry)

    # Create test state
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.3,
            "math.multiply": 0.3,
            "text.uppercase": 0.2,
            "text.split": 0.2
        }
    )

    print("\nInitial state:")
    probs = state.get_probability_distribution()
    for tool_id, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tool_id}: {prob:.4f}")

    # Define oracle: mark math tools as promising
    oracle = lambda tid: "math" in tid

    # Amplify
    amplified = amplifier.amplify_tools(state, oracle_fn=oracle, num_iterations=3)

    print("\nAfter amplitude amplification:")
    probs = amplified.get_probability_distribution()
    for tool_id, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True):
        print(f"  {tool_id}: {prob:.4f}")

    print(f"\nAmplification factor for marked tools: {amplifier.get_amplification_factor(amplified, ['math.add', 'math.multiply']):.4f}")


def demo_quantum_annealing():
    """Demo 5: Quantum Annealing Schedule."""
    print("\n" + "="*70)
    print("DEMO 5: Quantum Annealing Schedule (Algorithm 2.5)")
    print("="*70)

    registry = create_builtin_registry()
    annealer = QuantumAnnealingSchedule(registry)

    # Show temperature schedules
    schedules = annealer.compare_schedules(num_points=10)

    print("\nTemperature schedules (10 points):")
    print("Iter | Exponential | Linear   | Logarithmic | Adaptive")
    print("-"*60)
    for i in range(10):
        exp_t = next(t for it, t in schedules["exponential"] if it == i)
        lin_t = next(t for it, t in schedules["linear"] if it == i)
        log_t = next(t for it, t in schedules["logarithmic"] if it == i)
        ada_t = next(t for it, t in schedules["adaptive"] if it == i)
        print(f"{i:4d} | {exp_t:11.4f} | {lin_t:8.4f} | {log_t:11.4f} | {ada_t:8.4f}")

    # Test annealing convergence
    initial_state = QuantumState(
        tool_amplitudes={
            "tool1": 0.25,
            "tool2": 0.25,
            "tool3": 0.25,
            "tool4": 0.25
        },
        temperature=1.0
    )

    target = ["tool1", "tool2"]
    annealed = annealer.anneal_superposition(
        initial_state, target, schedule_type="exponential", num_steps=10
    )

    print(f"\nAnnealing toward target {target}:")
    print(f"  Initial convergence: {annealer.get_convergence_metric(initial_state, target):.4f}")
    print(f"  Final convergence: {annealer.get_convergence_metric(annealed, target):.4f}")


def demo_full_phase5_pipeline():
    """Demo: Full Phase 5 pipeline with all components."""
    print("\n" + "="*70)
    print("FULL PHASE 5 PIPELINE: Quantum-Inspired Tool Selection")
    print("="*70)

    registry = create_builtin_registry()

    # Step 1: Superposition
    print("\nStep 1: Create initial superposition")
    engine = SuperpositionEngine(registry)
    available_tools = ["math.add", "math.multiply", "text.uppercase", "text.split"]

    reasoning = {
        "reasoning_type": "multi-modal",
        "relevant_categories": ["math", "text"],
        "required_capabilities": ["analysis"]
    }
    consciousness_state = {
        "attention_focus": ["math"],
        "metacognitive_notes": ""
    }

    state = engine.create_initial_superposition(
        reasoning, consciousness_state, available_tools, initial_temperature=1.0
    )
    print(f"  Created superposition with entropy {state.get_entropy():.4f}")

    # Step 2: Entanglement
    print("\nStep 2: Apply entanglement coupling")
    entanglement = EntanglementMatrix(registry)
    matrix = entanglement.compute_entanglement_matrix(available_tools)
    state = entanglement.apply_entanglement_to_state(state, matrix)
    print(f"  Applied entanglement, entropy now {state.get_entropy():.4f}")

    # Step 3: Tunneling
    print("\nStep 3: Explore tunneling alternatives")
    explorer = TunnelingExplorer(registry)
    solutions, state = explorer.escape_local_optimum(
        ["math.add", "text.uppercase"], available_tools, state, escape_probability=0.5
    )
    print(f"  Found {len(solutions)} alternative configurations")

    # Step 4: Amplitude amplification
    print("\nStep 4: Amplify promising tools")
    amplifier = AmplitudeAmplifier(registry)
    oracle = lambda tid: "math" in tid
    state = amplifier.amplify_tools(state, oracle_fn=oracle, num_iterations=2)
    print(f"  Amplified math tools, entropy now {state.get_entropy():.4f}")

    # Step 5: Annealing
    print("\nStep 5: Anneal toward solution")
    annealer = QuantumAnnealingSchedule(registry)
    target = ["math.add", "math.multiply"]
    state = annealer.anneal_superposition(
        state, target, schedule_type="exponential", num_steps=5
    )
    convergence = annealer.get_convergence_metric(state, target)
    print(f"  Convergence to target: {convergence:.4f}")

    # Final measurement
    selected = engine.collapse_to_measurement(state, measurement_type="probabilistic", seed=42)
    print(f"\nFinal tool selection: {selected}")

    # Metrics
    print("\nPhase 5 Quantum Metrics:")
    metrics = compute_quantum_metrics(state)
    print(f"  Entropy: {metrics['entropy']:.4f}")
    print(f"  Purity: {metrics['purity']:.4f}")
    print(f"  Max probability: {metrics['max_probability']:.4f}")
    print(f"  Top tools: {[tid for tid, _ in metrics['top_tools'][:3]]}")


if __name__ == "__main__":
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "Phase 5: Quantum-Inspired AGI Framework" + " "*15 + "║")
    print("╚" + "="*68 + "╝")

    # Run demos
    demo_quantum_superposition()
    demo_quantum_entanglement()
    demo_quantum_tunneling()
    demo_quantum_amplification()
    demo_quantum_annealing()
    demo_full_phase5_pipeline()

    print("\n" + "="*70)
    print("✓ Phase 5 demonstration complete")
    print("="*70 + "\n")
