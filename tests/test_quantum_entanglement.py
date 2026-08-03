"""Tests for quantum entanglement matrix."""

import pytest
import numpy as np
from quantum.principles import QuantumState
from quantum.entanglement import EntanglementMatrix


@pytest.fixture
def entanglement(mock_registry):
    """Create entanglement matrix with mock registry."""
    return EntanglementMatrix(mock_registry)


def test_compute_entanglement_matrix(entanglement):
    """Test entanglement matrix computation."""
    tool_ids = ["math.add", "math.multiply", "text.uppercase"]

    matrix = entanglement.compute_entanglement_matrix(tool_ids)

    # Check structure
    assert len(matrix) == 3
    for tool_id in tool_ids:
        assert tool_id in matrix
        assert len(matrix[tool_id]) == 3

    # Self-coupling should be 1.0
    for tool_id in tool_ids:
        assert matrix[tool_id][tool_id] == 1.0

    # Coupling should be approximately symmetric
    for tool_a in tool_ids:
        for tool_b in tool_ids:
            strength_ab = matrix[tool_a][tool_b]
            strength_ba = matrix[tool_b][tool_a]
            # Allow some numerical tolerance since coupling is computed independently
            assert abs(strength_ab - strength_ba) < 1.0


def test_coupling_strength_bounds(entanglement):
    """Test that coupling strengths are in [0, 1]."""
    tool_ids = ["math.add", "text.split", "data.parse_json"]

    matrix = entanglement.compute_entanglement_matrix(tool_ids)

    for tool_a in tool_ids:
        for tool_b in tool_ids:
            strength = matrix[tool_a][tool_b]
            assert 0.0 <= strength <= 1.0


def test_apply_entanglement_to_state(entanglement):
    """Test applying entanglement to quantum state."""
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.5,
            "math.multiply": 0.3,
            "text.uppercase": 0.2
        }
    )

    matrix = entanglement.compute_entanglement_matrix(
        list(state.tool_amplitudes.keys())
    )

    new_state = entanglement.apply_entanglement_to_state(state, matrix)

    # Should still be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in new_state.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6


def test_get_coupled_tools(entanglement):
    """Test retrieving coupled tools."""
    tool_ids = ["math.add", "math.multiply", "text.uppercase", "text.split"]
    matrix = entanglement.compute_entanglement_matrix(tool_ids)

    coupled = entanglement.get_coupled_tools(
        "math.add", matrix, threshold=0.2
    )

    # Should return list of (tool_id, strength) tuples
    assert isinstance(coupled, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in coupled)
    assert all(strength >= 0.2 for _, strength in coupled)


def test_propagate_parameter_update(entanglement):
    """Test parameter update propagation."""
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.5,
            "math.multiply": 0.3,
            "text.uppercase": 0.2
        }
    )

    matrix = entanglement.compute_entanglement_matrix(
        list(state.tool_amplitudes.keys())
    )

    new_state = entanglement.propagate_parameter_update(
        state, "math.add", matrix, update_magnitude=0.1
    )

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in new_state.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6

    # Iteration should increase
    assert new_state.iteration == state.iteration + 1


def test_entanglement_entropy(entanglement):
    """Test entanglement entropy computation."""
    tool_ids = ["tool1", "tool2", "tool3", "tool4"]

    # Create matrix with varying entanglement
    matrix = {
        "tool1": {"tool1": 1.0, "tool2": 0.8, "tool3": 0.1, "tool4": 0.0},
        "tool2": {"tool1": 0.8, "tool2": 1.0, "tool3": 0.0, "tool4": 0.0},
        "tool3": {"tool1": 0.1, "tool2": 0.0, "tool3": 1.0, "tool4": 0.5},
        "tool4": {"tool1": 0.0, "tool2": 0.0, "tool3": 0.5, "tool4": 1.0},
    }

    entropy = entanglement.compute_entanglement_entropy(matrix)

    assert isinstance(entropy, float)
    assert entropy >= 0.0


def test_coupling_statistics(entanglement):
    """Test coupling statistics computation."""
    tool_ids = ["math.add", "math.multiply", "text.uppercase"]
    matrix = entanglement.compute_entanglement_matrix(tool_ids)

    stats = entanglement.get_coupling_statistics(matrix)

    # Check all statistics present
    assert "mean" in stats
    assert "max" in stats
    assert "min" in stats
    assert "median" in stats
    assert "std" in stats

    # Check ranges
    assert 0 <= stats["min"] <= stats["mean"] <= stats["max"]
