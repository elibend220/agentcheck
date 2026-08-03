"""Tests for Phase 5 integration with earlier phases."""

import pytest
from quantum.principles import QuantumState, QuantumPhase5State
from quantum.superposition import SuperpositionEngine
from quantum.entanglement import EntanglementMatrix
from quantum.tunneling import TunnelingExplorer
from quantum.amplitude_amplification import AmplitudeAmplifier
from quantum.annealing import QuantumAnnealingSchedule


@pytest.fixture
def phase5_components(mock_registry):
    """Create all Phase 5 components."""
    return {
        "superposition": SuperpositionEngine(mock_registry),
        "entanglement": EntanglementMatrix(mock_registry),
        "tunneling": TunnelingExplorer(mock_registry),
        "amplifier": AmplitudeAmplifier(mock_registry),
        "annealer": QuantumAnnealingSchedule(mock_registry),
    }


def test_phase5_state_creation():
    """Test creating Phase 5 state object."""
    quantum_state = QuantumState(
        tool_amplitudes={
            "math.add": 0.6,
            "text.uppercase": 0.4
        }
    )

    phase5_state = QuantumPhase5State(
        quantum_amplitudes=quantum_state.tool_amplitudes,
        entanglement_matrix={},
        temperature=1.0,
        amplification_iterations=2,
        quantum_metrics={"entropy": 0.8}
    )

    assert phase5_state.temperature == 1.0
    assert phase5_state.amplification_iterations == 2
    assert "entropy" in phase5_state.quantum_metrics


def test_phase5_state_serialization():
    """Test Phase 5 state serialization."""
    phase5_state = QuantumPhase5State(
        quantum_amplitudes={"tool1": 0.5 + 0.3j, "tool2": 0.4 + 0.1j},
        entanglement_matrix={"tool1": {"tool1": 1.0, "tool2": 0.3}},
        temperature=0.5,
        tunneling_solutions=[{"config": ["tool1"], "energy": -1.0}],
        quantum_metrics={"entropy": 1.2}
    )

    serialized = phase5_state.to_dict()

    assert isinstance(serialized, dict)
    assert "quantum_amplitudes" in serialized
    assert "real" in serialized["quantum_amplitudes"]["tool1"]
    assert "imag" in serialized["quantum_amplitudes"]["tool1"]


def test_full_phase5_pipeline(phase5_components):
    """Test full Phase 5 pipeline."""
    available_tools = ["math.add", "math.multiply", "text.uppercase"]

    # Step 1: Create superposition
    reasoning = {
        "reasoning_type": "causal",
        "relevant_categories": ["math"],
        "required_capabilities": []
    }
    consciousness_state = {
        "attention_focus": ["math"],
        "metacognitive_notes": ""
    }

    state = phase5_components["superposition"].create_initial_superposition(
        reasoning, consciousness_state, available_tools, initial_temperature=1.0
    )

    # Step 2: Compute entanglement
    entanglement_matrix = phase5_components["entanglement"].compute_entanglement_matrix(
        available_tools
    )
    state = phase5_components["entanglement"].apply_entanglement_to_state(
        state, entanglement_matrix
    )

    # Step 3: Apply tunneling
    tunneling_solutions, state = phase5_components["tunneling"].escape_local_optimum(
        ["math.add"], available_tools, state, escape_probability=0.5
    )

    # Step 4: Amplify promising tools
    oracle = lambda tid: "math" in tid
    state = phase5_components["amplifier"].amplify_tools(
        state, oracle_fn=oracle, num_iterations=2
    )

    # Step 5: Anneal toward solution
    state = phase5_components["annealer"].apply_annealing_to_state(
        state, schedule_type="exponential", total_iterations=10
    )

    # Verify final state is valid
    assert isinstance(state, QuantumState)
    total_prob = sum(abs(amp) ** 2 for amp in state.tool_amplitudes.values())
    assert abs(total_prob - 1.0) < 1e-6


def test_phase5_state_update_pattern(phase5_components):
    """Test preserving Phase 5 state through updates."""
    initial_state = QuantumState(
        tool_amplitudes={"tool1": 0.5, "tool2": 0.5},
        temperature=1.0,
        iteration=0
    )

    # Simulate state updates through pipeline
    state = initial_state
    for i in range(3):
        state = QuantumState(
            tool_amplitudes=state.tool_amplitudes,
            parameter_couplings=state.parameter_couplings,
            temperature=state.temperature * 0.9,
            iteration=i + 1,
            history=state.history,
        )

    assert state.iteration == 3
    assert state.temperature < initial_state.temperature


def test_quantum_metrics_integration():
    """Test quantum metrics computation."""
    from quantum.metrics import compute_quantum_metrics

    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.6,
            "tool2": 0.3,
            "tool3": 0.1
        },
        temperature=0.5,
        iteration=10
    )

    metrics = compute_quantum_metrics(state)

    assert isinstance(metrics, dict)
    assert "entropy" in metrics
    assert "purity" in metrics
    assert "temperature" in metrics
    assert "iteration" in metrics
    assert "top_tools" in metrics
    assert len(metrics["top_tools"]) <= 5


def test_quantum_phase5_state_integration():
    """Test integrating QuantumPhase5State with results."""
    phase5_state = QuantumPhase5State(
        quantum_amplitudes={"tool1": 0.7, "tool2": 0.3},
        entanglement_matrix={},
        temperature=0.1,
        amplification_iterations=5,
        tunneling_solutions=[],
        quantum_metrics={"entropy": 0.5, "purity": 0.9}
    )

    # Should be convertible to dict for state tracking
    state_dict = phase5_state.to_dict()
    assert isinstance(state_dict, dict)
    assert state_dict["temperature"] == 0.1


def test_multi_phase_state_fusion(phase5_components):
    """Test fusing Phase 1-3 state with Phase 5 quantum state."""
    # Simulated Phase 1-3 output
    phase_1_3_state = {
        "input_text": "test query",
        "intent": "analyze data",
        "entities": ["data"],
        "reasoning_type": "logical",
        "reasoning_conclusion": "should use logic tools",
        "creative_ideas": ["combine tools"],
        "selected_tools": None,  # Not selected yet
    }

    # Phase 5 quantum state
    quantum_state = QuantumState(
        tool_amplitudes={
            "logic.if_then": 0.5,
            "logic.compare": 0.3,
            "math.add": 0.2
        },
        temperature=1.0
    )

    # Should be able to use Phase 5 to enhance tool selection
    top_tools = quantum_state.get_top_tools(k=3)
    assert len(top_tools) > 0
    assert all(isinstance(tool_id, str) for tool_id, _ in top_tools)
