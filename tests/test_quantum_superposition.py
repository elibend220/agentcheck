"""Tests for quantum superposition engine."""

import pytest
import numpy as np
from quantum.principles import QuantumState, normalize_amplitudes
from quantum.superposition import SuperpositionEngine


@pytest.fixture
def engine(mock_registry):
    """Create superposition engine with mock registry."""
    return SuperpositionEngine(mock_registry)


def test_create_initial_superposition(engine):
    """Test initial superposition creation."""
    reasoning = {
        "reasoning_type": "causal",
        "relevant_categories": ["math", "text"],
        "required_capabilities": ["analysis", "reasoning"]
    }
    consciousness_state = {
        "attention_focus": ["math", "addition"],
        "metacognitive_notes": "weak understanding"
    }
    available_tools = ["math.add", "math.multiply", "text.uppercase"]

    state = engine.create_initial_superposition(
        reasoning,
        consciousness_state,
        available_tools,
        initial_temperature=1.0
    )

    # Check state properties
    assert isinstance(state, QuantumState)
    assert len(state.tool_amplitudes) == 3
    assert state.temperature == 1.0

    # Check normalization: Σ|α_i|² = 1
    total_prob = sum(abs(amp) ** 2 for amp in state.tool_amplitudes.values())
    assert abs(total_prob - 1.0) < 1e-6

    # Check all tools have non-zero amplitude
    for amp in state.tool_amplitudes.values():
        assert abs(amp) > 0


def test_empty_tool_list(engine):
    """Test superposition with no tools."""
    state = engine.create_initial_superposition(
        reasoning={},
        consciousness_state={},
        available_tools=[]
    )

    assert state.tool_amplitudes == {}
    assert state.temperature == 1.0


def test_consciousness_modulation(engine):
    """Test consciousness modulation of amplitudes."""
    initial_state = QuantumState(
        tool_amplitudes={
            "math.add": 0.5,
            "text.uppercase": 0.3,
            "math.multiply": 0.2
        }
    )

    consciousness_state = {
        "attention_focus": ["math", "addition"],
        "metacognitive_notes": "uncertain about this"
    }

    modulated_state = engine.apply_consciousness_modulation(
        initial_state,
        consciousness_state
    )

    # State should still be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in modulated_state.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6


def test_superposition_entropy(engine):
    """Test entropy computation."""
    # Pure state
    pure_state = QuantumState(
        tool_amplitudes={"tool1": 1.0, "tool2": 0.0, "tool3": 0.0}
    )
    assert pure_state.get_entropy() < 0.1

    # Maximally mixed state
    mixed_state = QuantumState(
        tool_amplitudes={
            "tool1": 1.0 / np.sqrt(3),
            "tool2": 1.0 / np.sqrt(3),
            "tool3": 1.0 / np.sqrt(3)
        }
    )
    assert mixed_state.get_entropy() > 1.4


def test_collapse_to_measurement(engine):
    """Test measurement and collapse."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.5,
            "tool2": 0.3,
            "tool3": 0.2
        }
    )

    # Probabilistic measurement
    selected_prob = engine.collapse_to_measurement(
        state,
        measurement_type="probabilistic",
        seed=42
    )
    assert len(selected_prob) <= 3
    assert all(isinstance(tid, str) for tid in selected_prob)
    assert len(selected_prob) > 0

    # Deterministic measurement
    selected_det = engine.collapse_to_measurement(
        state,
        measurement_type="deterministic"
    )
    assert "tool1" in selected_det
    assert len(selected_det) <= 3

    # Threshold measurement
    selected_thresh = engine.collapse_to_measurement(
        state,
        measurement_type="threshold"
    )
    assert len(selected_thresh) >= 1


def test_measurement_reproducibility(engine):
    """Test that measurements with same seed are reproducible."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.6,
            "tool2": 0.3,
            "tool3": 0.1
        }
    )

    result1 = engine.collapse_to_measurement(state, seed=123)
    result2 = engine.collapse_to_measurement(state, seed=123)

    assert result1 == result2


def test_get_dominant_tools(engine):
    """Test retrieving dominant tools."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.5,
            "tool2": 0.3,
            "tool3": 0.15,
            "tool4": 0.05
        }
    )

    top_2 = engine.get_dominant_tools(state, k=2)

    assert len(top_2) == 2
    assert top_2[0][0] == "tool1"
    assert top_2[1][0] == "tool2"
    assert top_2[0][1] > top_2[1][1]
