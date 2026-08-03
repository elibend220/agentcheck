"""Tests for quantum annealing schedule."""

import pytest
import numpy as np
from quantum.principles import QuantumState
from quantum.annealing import QuantumAnnealingSchedule


@pytest.fixture
def annealer(mock_registry):
    """Create annealing schedule with mock registry."""
    return QuantumAnnealingSchedule(mock_registry)


def test_exponential_schedule(annealer):
    """Test exponential temperature schedule."""
    temps = [
        annealer.compute_temperature(
            i,
            schedule_type="exponential",
            initial_temperature=1.0,
            final_temperature=0.01,
            total_iterations=100
        )
        for i in range(101)
    ]

    # Temperature should decrease
    assert temps[0] > temps[50] > temps[100]

    # Should approach final temperature
    assert temps[-1] < 0.05


def test_linear_schedule(annealer):
    """Test linear temperature schedule."""
    temps = [
        annealer.compute_temperature(
            i,
            schedule_type="linear",
            initial_temperature=1.0,
            final_temperature=0.0,
            total_iterations=100
        )
        for i in range(101)
    ]

    # Should be monotonically decreasing
    assert all(temps[i] >= temps[i + 1] for i in range(len(temps) - 1))


def test_logarithmic_schedule(annealer):
    """Test logarithmic temperature schedule."""
    temps = [
        annealer.compute_temperature(
            i,
            schedule_type="logarithmic",
            initial_temperature=1.0,
            total_iterations=100
        )
        for i in range(1, 101)
    ]

    # Should decrease, slower than exponential
    assert all(temps[i] >= temps[i + 1] for i in range(len(temps) - 1))


def test_adaptive_schedule(annealer):
    """Test adaptive temperature schedule."""
    temps = [
        annealer.compute_temperature(
            i,
            schedule_type="adaptive",
            initial_temperature=1.0,
            total_iterations=100
        )
        for i in range(101)
    ]

    # Should be monotonically decreasing
    assert all(temps[i] >= temps[i + 1] for i in range(len(temps) - 1))
    assert temps[-1] < 0.1


def test_apply_annealing_to_state(annealer):
    """Test applying annealing to state."""
    state = QuantumState(
        tool_amplitudes={"tool1": 0.5, "tool2": 0.5},
        iteration=10,
        temperature=1.0
    )

    new_state = annealer.apply_annealing_to_state(
        state,
        schedule_type="exponential",
        total_iterations=100
    )

    # Temperature should decrease
    assert new_state.temperature < state.temperature

    # Amplitudes should be unchanged
    assert new_state.tool_amplitudes == state.tool_amplitudes


def test_metropolis_accept_better(annealer):
    """Test Metropolis acceptance of better solution."""
    accepted = annealer.metropolis_accept(
        current_energy=2.0,
        proposed_energy=1.0,
        temperature=1.0
    )

    assert accepted


def test_metropolis_accept_worse(annealer):
    """Test Metropolis acceptance of worse solution."""
    # With low temperature, worse solutions rejected
    for _ in range(10):
        accepted = annealer.metropolis_accept(
            current_energy=1.0,
            proposed_energy=2.0,
            temperature=0.01
        )
        if not accepted:
            break

    # Most should be rejected
    rejections = sum(
        1 for _ in range(10)
        if not annealer.metropolis_accept(1.0, 2.0, 0.01)
    )
    assert rejections > 7


def test_anneal_superposition(annealer):
    """Test annealing toward target configuration."""
    state = QuantumState(
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
        state,
        target,
        schedule_type="exponential",
        num_steps=20
    )

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in annealed.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6

    # Target tools should have higher probability
    probs = annealed.get_probability_distribution()
    target_prob = sum(probs.get(tid, 0) for tid in target)
    initial_target_prob = sum(
        state.get_probability_distribution().get(tid, 0) for tid in target
    )
    assert target_prob > initial_target_prob


def test_convergence_metric(annealer):
    """Test convergence metric computation."""
    state = QuantumState(
        tool_amplitudes={
            "target1": 0.7 + 0.0j,
            "target2": 0.7 + 0.0j,
            "other": 0.0 + 0.0j
        }
    )

    convergence = annealer.get_convergence_metric(
        state,
        ["target1", "target2"]
    )

    assert 0.0 <= convergence <= 1.0
    assert convergence > 0.9


def test_convergence_metric_poor(annealer):
    """Test convergence metric for poor alignment."""
    state = QuantumState(
        tool_amplitudes={
            "target1": 0.1,
            "target2": 0.1,
            "other1": 0.4,
            "other2": 0.4
        }
    )

    convergence = annealer.get_convergence_metric(
        state,
        ["target1", "target2"]
    )

    assert convergence < 0.3


def test_get_schedule_trajectory(annealer):
    """Test getting schedule trajectory."""
    trajectory = annealer.get_schedule_trajectory(
        schedule_type="exponential",
        num_points=10
    )

    assert len(trajectory) == 10
    assert all(isinstance(point, tuple) and len(point) == 2 for point in trajectory)

    # Temperatures should decrease
    temps = [t for _, t in trajectory]
    assert all(temps[i] >= temps[i + 1] for i in range(len(temps) - 1))


def test_compare_schedules(annealer):
    """Test comparing all schedule types."""
    schedules = annealer.compare_schedules(num_points=20)

    assert len(schedules) == 4
    assert "exponential" in schedules
    assert "linear" in schedules
    assert "logarithmic" in schedules
    assert "adaptive" in schedules

    for schedule_name, trajectory in schedules.items():
        assert len(trajectory) == 20
