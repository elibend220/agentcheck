"""Tests for Phase 5 vs Phase 4 comparison."""

import pytest
from quantum.metrics import compare_phase4_vs_phase5, analyze_quantum_trajectory
from quantum.principles import QuantumState


def test_phase4_vs_phase5_comparison():
    """Test comparing Phase 4 and Phase 5 results."""
    phase4_result = {
        "selected_tools": ["math.add", "text.uppercase"],
        "execution_time": 2.5,
        "error_log": [],
        "verified_results": 2
    }

    phase5_result = {
        "selected_tools": ["math.add"],
        "execution_time": 2.0,
        "error_log": [],
        "verified_results": 1
    }

    phase4_tools = ["math.add", "text.uppercase"]
    phase5_tools = ["math.add"]

    comparison = compare_phase4_vs_phase5(
        phase4_result,
        phase5_result,
        phase4_tools,
        phase5_tools
    )

    assert isinstance(comparison, dict)
    assert "phase4" in comparison
    assert "phase5" in comparison
    assert "overall_score" in comparison

    # Phase 5 should be more efficient (fewer tools)
    assert comparison["phase5"]["tool_count"] <= comparison["phase4"]["tool_count"]


def test_phase4_vs_phase5_with_errors():
    """Test comparison with different error counts."""
    phase4_result = {
        "error_log": [{"error": "tool failed"}, {"error": "timeout"}],
        "execution_time": 3.0
    }

    phase5_result = {
        "error_log": [{"error": "validation failed"}],
        "execution_time": 2.5
    }

    comparison = compare_phase4_vs_phase5(
        phase4_result,
        phase5_result,
        ["tool1", "tool2", "tool3"],
        ["tool1", "tool2"]
    )

    # Phase 5 should have better error reduction score
    assert comparison["errors"]["phase4"] > comparison["errors"]["phase5"]


def test_efficiency_improvement():
    """Test efficiency improvement metric."""
    phase4_result = {"error_log": []}
    phase5_result = {"error_log": []}

    # Phase 5 uses fewer tools
    comparison = compare_phase4_vs_phase5(
        phase4_result,
        phase5_result,
        ["t1", "t2", "t3", "t4"],  # Phase 4: 4 tools
        ["t1", "t2"]  # Phase 5: 2 tools
    )

    # Efficiency improvement should be positive
    assert comparison["efficiency_improvement"] >= 0


def test_coverage_metrics():
    """Test coverage computation in comparison."""
    comparison = compare_phase4_vs_phase5(
        {"error_log": []},
        {"error_log": []},
        ["tool1", "tool2"],
        ["tool1"]
    )

    assert "coverage" in comparison
    assert "phase4" in comparison["coverage"]
    assert "phase5" in comparison["coverage"]
    assert "improvement" in comparison["coverage"]


def test_diversity_metrics():
    """Test diversity computation in comparison."""
    comparison = compare_phase4_vs_phase5(
        {"error_log": []},
        {"error_log": []},
        ["math.add", "math.multiply", "text.uppercase", "text.split"],
        ["math.add", "text.uppercase"]
    )

    assert "diversity" in comparison
    assert comparison["diversity"]["phase4"] >= 0
    assert comparison["diversity"]["phase5"] >= 0


def test_analyze_quantum_trajectory():
    """Test analyzing quantum trajectory."""
    history = [
        {
            "iteration": 0,
            "temperature": 1.0,
            "best_energy": -5.0,
            "purity": 0.3,
            "entropy": 2.0
        },
        {
            "iteration": 5,
            "temperature": 0.5,
            "best_energy": -7.0,
            "purity": 0.6,
            "entropy": 1.5
        },
        {
            "iteration": 10,
            "temperature": 0.1,
            "best_energy": -8.0,
            "purity": 0.95,
            "entropy": 0.3
        }
    ]

    analysis = analyze_quantum_trajectory(history)

    assert isinstance(analysis, dict)
    assert "total_iterations" in analysis
    assert "temperature_trajectory" in analysis
    assert "energy_trajectory" in analysis
    assert "purity_trajectory" in analysis
    assert "entropy_trajectory" in analysis

    # Check convergence
    assert analysis["energy_trajectory"]["improvement"] > 0
    assert analysis["purity_trajectory"]["final"] > analysis["purity_trajectory"]["initial"]


def test_empty_trajectory_analysis():
    """Test analyzing empty trajectory."""
    analysis = analyze_quantum_trajectory([])

    assert isinstance(analysis, dict)
    assert len(analysis) == 0


def test_overall_score_computation():
    """Test overall score reflects improvement."""
    # Phase 5 better on all metrics
    comparison_good = compare_phase4_vs_phase5(
        {"error_log": [1, 2, 3]},  # 3 errors
        {"error_log": [1]},  # 1 error
        ["t1", "t2", "t3"],  # 3 tools
        ["t1"]  # 1 tool
    )

    # Phase 4 better on all metrics
    comparison_bad = compare_phase4_vs_phase5(
        {"error_log": [1]},
        {"error_log": [1, 2, 3]},
        ["t1"],
        ["t1", "t2", "t3"]
    )

    # Good comparison should have higher score
    assert comparison_good["overall_score"] > comparison_bad["overall_score"]


def test_convergence_rate_computation():
    """Test convergence rate in trajectory analysis."""
    history = [
        {"iteration": 0, "best_energy": 0.0},
        {"iteration": 1, "best_energy": -0.5},
        {"iteration": 2, "best_energy": -1.0},
        {"iteration": 3, "best_energy": -1.2},
        {"iteration": 4, "best_energy": -1.3},
    ]

    analysis = analyze_quantum_trajectory(history)

    if "convergence_rate" in analysis:
        assert analysis["convergence_rate"] > 0
