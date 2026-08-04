"""Tests for quantum tunneling explorer."""

import pytest
import numpy as np
from quantum.principles import QuantumState
from quantum.tunneling import TunnelingExplorer


@pytest.fixture
def explorer(mock_registry):
    """Create tunneling explorer with mock registry."""
    return TunnelingExplorer(mock_registry)


def test_find_tunneling_paths(explorer):
    """Test finding tunneling paths."""
    current_tools = ["math.add", "text.uppercase"]
    available_tools = ["math.add", "math.multiply", "text.uppercase", "text.split"]

    solutions = explorer.find_tunneling_paths(
        current_tools,
        available_tools,
        energy_limit=5.0,
        max_substitutions=2
    )

    # Should find some alternatives
    assert isinstance(solutions, list)
    if solutions:
        for sol in solutions:
            assert "config" in sol
            assert "energy" in sol
            assert "jump_distance" in sol
            assert "explanation" in sol


def test_tunneling_paths_structure(explorer):
    """Test structure of tunneling solutions."""
    current = ["tool1"]
    available = ["tool1", "tool2", "tool3"]

    solutions = explorer.find_tunneling_paths(current, available)

    if solutions:
        for sol in solutions:
            assert isinstance(sol["config"], list)
            assert isinstance(sol["energy"], (int, float))
            assert isinstance(sol["jump_distance"], int)
            assert isinstance(sol["explanation"], str)


def test_apply_tunneling_to_state(explorer):
    """Test applying tunneling to quantum state."""
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.6,
            "text.uppercase": 0.4
        }
    )

    tunneling_solutions = [
        {
            "config": ["math.multiply", "text.uppercase"],
            "energy": -2.0,
            "jump_distance": 1
        },
        {
            "config": ["math.add", "text.split"],
            "energy": -1.5,
            "jump_distance": 1
        }
    ]

    new_state = explorer.apply_tunneling_to_state(
        state,
        tunneling_solutions,
        tunneling_temperature=1.0
    )

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in new_state.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6

    # Iteration should increase
    assert new_state.iteration == state.iteration + 1


def test_escape_local_optimum(explorer):
    """Test escaping local optimum."""
    current = ["math.add", "text.uppercase"]
    available = ["math.add", "math.multiply", "text.uppercase", "text.split"]

    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.6,
            "text.uppercase": 0.4
        }
    )

    solutions, new_state = explorer.escape_local_optimum(
        current,
        available,
        state,
        escape_probability=1.0  # Force escape
    )

    assert isinstance(solutions, list)
    assert isinstance(new_state, QuantumState)


def test_barrier_height(explorer):
    """Test barrier height computation."""
    source = ["math.add", "text.uppercase"]
    target = ["math.multiply", "text.split"]

    barrier = explorer.compute_barrier_height(source, target)

    assert isinstance(barrier, float)
    assert barrier >= 0.0


def test_tunneling_probability(explorer):
    """Test tunneling probability computation."""
    barrier = 2.0
    distance = 1
    temperature = 1.0

    prob = explorer.compute_tunneling_probability(
        barrier, distance, temperature
    )

    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0

    # Higher barrier should give lower probability
    prob_high_barrier = explorer.compute_tunneling_probability(
        5.0, distance, temperature
    )
    assert prob_high_barrier < prob

    # Higher temperature should give higher probability
    prob_high_temp = explorer.compute_tunneling_probability(
        barrier, distance, 5.0
    )
    assert prob_high_temp > prob


def test_zero_temperature_tunneling(explorer):
    """Test tunneling with zero temperature."""
    barrier = 2.0
    distance = 1

    prob = explorer.compute_tunneling_probability(
        barrier, distance, temperature=0.0
    )

    assert prob == 0.0


def test_tunneling_statistics(explorer):
    """Test tunneling statistics."""
    current = ["math.add", "text.uppercase"]
    available = ["math.add", "math.multiply", "text.uppercase", "text.split"]

    stats = explorer.get_tunneling_statistics(current, available)

    assert isinstance(stats, dict)
    assert "escape_routes" in stats
    assert "min_barrier" in stats
    assert "max_barrier" in stats
    assert "avg_barrier" in stats
    assert "landscape_complexity" in stats

    if stats["escape_routes"] > 0:
        assert stats["min_barrier"] <= stats["avg_barrier"] <= stats["max_barrier"]


def test_distance_affects_probability(explorer):
    """Test that distance affects tunneling probability."""
    barrier = 1.0
    temp = 1.0

    prob_dist1 = explorer.compute_tunneling_probability(barrier, 1, temp)
    prob_dist2 = explorer.compute_tunneling_probability(barrier, 2, temp)

    assert prob_dist1 > prob_dist2
