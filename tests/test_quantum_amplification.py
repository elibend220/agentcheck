"""Tests for quantum amplitude amplification."""

import pytest
import numpy as np
from quantum.principles import QuantumState
from quantum.amplitude_amplification import AmplitudeAmplifier


@pytest.fixture
def amplifier(mock_registry):
    """Create amplitude amplifier with mock registry."""
    return AmplitudeAmplifier(mock_registry)


def test_mark_promising_tools_default(amplifier):
    """Test marking tools with default oracle."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.6 + 0.0j,
            "tool2": 0.3 + 0.0j,
            "tool3": 0.1 + 0.0j
        }
    )

    marked, new_state = amplifier.mark_promising_tools(
        state,
        oracle_fn=None,
        threshold=0.15
    )

    # Should mark tools above threshold
    assert "tool1" in marked
    assert len(marked) >= 1

    # Phase should be inverted for at least one marked tool
    if "tool1" in marked:
        old_phase = np.angle(state.tool_amplitudes["tool1"])
        new_phase = np.angle(new_state.tool_amplitudes["tool1"])
        # Phase should change (either +pi or -pi in the complex plane)
        assert old_phase != new_phase


def test_mark_promising_tools_custom_oracle(amplifier):
    """Test marking tools with custom oracle."""
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.4,
            "text.uppercase": 0.3,
            "math.multiply": 0.3
        }
    )

    # Mark math tools only
    oracle = lambda tid: "math" in tid

    marked, new_state = amplifier.mark_promising_tools(
        state,
        oracle_fn=oracle
    )

    assert "math.add" in marked
    assert "math.multiply" in marked
    assert "text.uppercase" not in marked


def test_amplify_iteration(amplifier):
    """Test single amplification iteration."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.5,
            "tool2": 0.3,
            "tool3": 0.2
        }
    )

    marked_tools = ["tool1"]
    amplified = amplifier.amplify_iteration(state, marked_tools)

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in amplified.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6

    # Iteration should increase
    assert amplified.iteration == state.iteration + 1


def test_amplify_tools(amplifier):
    """Test full amplification procedure."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.4,
            "tool2": 0.3,
            "tool3": 0.2,
            "tool4": 0.1
        }
    )

    oracle = lambda tid: tid in ["tool1", "tool2"]

    amplified = amplifier.amplify_tools(
        state,
        oracle_fn=oracle,
        num_iterations=3
    )

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in amplified.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6

    # Marked tools should have higher probability
    probs = amplified.get_probability_distribution()
    assert probs["tool1"] + probs["tool2"] >= state.get_probability_distribution()["tool1"] + state.get_probability_distribution()["tool2"]


def test_amplify_by_energy(amplifier):
    """Test amplitude amplification by energy."""
    state = QuantumState(
        tool_amplitudes={
            "math.add": 0.3,
            "math.multiply": 0.3,
            "text.uppercase": 0.2,
            "text.split": 0.2
        }
    )

    amplified = amplifier.amplify_by_energy(state, temperature=1.0)

    # Should be normalized
    total_prob = sum(
        abs(amp) ** 2 for amp in amplified.tool_amplitudes.values()
    )
    assert abs(total_prob - 1.0) < 1e-6


def test_optimal_iterations_computation(amplifier):
    """Test optimal iteration count."""
    # Few marked tools in large set
    iters_low = amplifier._compute_optimal_iterations(2, 10)
    assert iters_low >= 1

    # Many marked tools in small set
    iters_high = amplifier._compute_optimal_iterations(8, 10)
    assert iters_high >= 1

    # Single marked tool
    iters_single = amplifier._compute_optimal_iterations(1, 10)
    assert iters_single > iters_low


def test_get_amplification_factor(amplifier):
    """Test amplification factor computation."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.6,
            "tool2": 0.2,
            "tool3": 0.2
        }
    )

    marked = ["tool1"]
    factor = amplifier.get_amplification_factor(state, marked)

    assert isinstance(factor, float)
    assert factor >= 1.0


def test_amplification_factor_empty_marked(amplifier):
    """Test amplification factor with no marked tools."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.5,
            "tool2": 0.5
        }
    )

    factor = amplifier.get_amplification_factor(state, [])
    assert factor == 1.0


def test_compute_amplification_steps(amplifier):
    """Test tracing amplification steps."""
    state = QuantumState(
        tool_amplitudes={
            "tool1": 0.3 + 0.0j,
            "tool2": 0.3 + 0.0j,
            "tool3": 0.2 + 0.0j,
            "tool4": 0.2 + 0.0j
        }
    )

    oracle = lambda tid: tid in ["tool1", "tool2"]

    steps = amplifier.compute_amplification_steps(
        state,
        oracle,
        max_iterations=10
    )

    assert len(steps) > 0
    assert all(len(step) == 3 for step in steps)

    # Amplification factor should be computed for each step
    factors = [step[1] for step in steps]
    assert all(isinstance(f, float) for f in factors)

    # Entropy should be computed for each step
    entropies = [step[2] for step in steps]
    assert all(isinstance(e, float) for e in entropies)
