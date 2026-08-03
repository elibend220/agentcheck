"""Tests for Phase 16: System Engineering & Self-Optimization."""
import pytest
from agents.phase16_system_engineering import (
    make_metrics_collection_node,
    make_architecture_analysis_node,
    make_optimization_recommendation_node,
    make_adaptive_configurator_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Analyze system performance metrics" in prompt:
        return """PHASE_LATENCIES: [phase1: 50ms, phase4: 120ms, phase6: 80ms]
SUCCESS_RATES: [phase1: 98%, phase4: 92%, phase6: 95%]
NODE_EXECUTION_COUNTS: [nlp: 1, tool_selection: 1, learning: 1]
RESOURCE_USAGE: [memory_mb: 256, cpu_percent: 45]
BOTTLENECK_PHASES: [phase4, phase5]
CONFIDENCE: 0.87"""
    elif "Analyze system architecture" in prompt:
        return """CRITICAL_PHASES: [phase1, phase4, phase6]
LOW_IMPACT_PHASES: [phase3c_creativity, phase14_streaming]
PHASE_COUPLING: [phase4 depends on phase1, phase6 depends on phase4]
OPPORTUNITIES: [Optimize phase4 execution, Reduce phase5 overhead]
CONFIDENCE: 0.85"""
    elif "Generate system optimization recommendations" in prompt:
        return """PHASE_CHANGES: [Enable phase16 optimization, Adjust phase4 parameters]
ROUTING_CHANGES: [Optimize phase 1->4 transition, Add fast-path for common cases]
RESOURCE_ALLOCATION: [Increase phase4 memory to 512mb, Reduce phase3 CPU]
PRIORITY: [Critical: phase4 optimization, Medium: routing improvements]
CONFIDENCE: 0.83"""
    elif "Apply system optimizations" in prompt:
        return """APPLIED_CHANGES: [Phase4 optimization applied, Resource allocation updated]
IMPACT: [Expected latency reduction 15%, Success rate improvement 3%]
READY: true
CONFIDENCE: 0.82"""
    return ""


def test_metrics_collection_node():
    """Test Phase 16a metrics collection node."""
    node = make_metrics_collection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Collect metrics",
        "execution_history": [{"phase": "1", "latency": 50}] * 10,
    }

    result = node(state)

    assert result["metrics_collection_confidence"] > 0.8
    assert len(result["bottleneck_phases"]) > 0
    assert "phase4" in result["bottleneck_phases"][0]


def test_metrics_collection_node_empty():
    """Test metrics collection with no execution history."""
    node = make_metrics_collection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty metrics",
    }

    result = node(state)

    assert isinstance(result["phase_latencies"], dict)
    assert isinstance(result["phase_success_rates"], dict)
    assert isinstance(result["metrics_collection_confidence"], float)


def test_architecture_analysis_node():
    """Test Phase 16b architecture analysis node."""
    node = make_architecture_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Analyze architecture",
        "phase_latencies": {"phase1": 50, "phase4": 120, "phase6": 80},
        "phase_success_rates": {"phase1": 0.98, "phase4": 0.92, "phase6": 0.95},
    }

    result = node(state)

    assert result["architecture_analysis_confidence"] > 0.8
    assert len(result["critical_phases"]) > 0
    assert len(result["optimization_opportunities"]) > 0


def test_architecture_analysis_node_empty():
    """Test architecture analysis with no metrics."""
    node = make_architecture_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty analysis",
        "phase_latencies": {},
        "phase_success_rates": {},
    }

    result = node(state)

    assert result["critical_phases"] == []
    assert result["low_impact_phases"] == []
    assert result["architecture_analysis_confidence"] == 0.0


def test_optimization_recommendation_node():
    """Test Phase 16c optimization recommendation node."""
    node = make_optimization_recommendation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Generate recommendations",
        "optimization_opportunities": ["Optimize phase4", "Reduce phase5 overhead"],
        "critical_phases": ["phase1", "phase4"],
        "low_impact_phases": ["phase3c"],
    }

    result = node(state)

    assert result["optimization_recommendation_confidence"] > 0.8
    assert len(result["recommended_phase_changes"]) > 0
    assert len(result["recommended_routing_changes"]) > 0


def test_optimization_recommendation_node_empty():
    """Test optimization recommendation with no analysis."""
    node = make_optimization_recommendation_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Empty recommendations",
        "optimization_opportunities": [],
        "critical_phases": [],
        "low_impact_phases": [],
    }

    result = node(state)

    assert result["recommended_phase_changes"] == []
    assert result["recommended_routing_changes"] == []
    assert result["optimization_recommendation_confidence"] == 0.0


def test_adaptive_configurator_node():
    """Test Phase 16d adaptive configurator node."""
    node = make_adaptive_configurator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Apply optimizations",
        "recommended_phase_changes": ["Enable phase16 optimization"],
        "recommended_routing_changes": ["Optimize phase 1->4 transition"],
        "recommended_resource_allocation": {"phase4_memory": 512},
        "phase_latencies": {"phase1": 50, "phase4": 120},
        "bottleneck_phases": ["phase4", "phase5"],
        "critical_phases": ["phase1", "phase4"],
    }

    result = node(state)

    assert result["system_optimized"] is True
    assert "System Engineering" in result["phase16_summary"]
    assert len(result["applied_optimizations"]) > 0


def test_adaptive_configurator_node_minimal():
    """Test adaptive configurator with minimal data."""
    node = make_adaptive_configurator_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Minimal config",
    }

    result = node(state)

    assert result["system_optimized"] is True
    assert "System Engineering" in result["phase16_summary"]


def test_metrics_parsing():
    """Test metrics response parsing."""
    node = make_metrics_collection_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
    }

    result = node(state)

    assert isinstance(result["phase_latencies"], dict)
    assert isinstance(result["phase_success_rates"], dict)
    assert isinstance(result["bottleneck_phases"], list)
    for latency in result["phase_latencies"].values():
        assert isinstance(latency, float)


def test_architecture_analysis_parsing():
    """Test architecture analysis parsing."""
    node = make_architecture_analysis_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
        "phase_latencies": {"phase1": 50},
        "phase_success_rates": {"phase1": 0.98},
    }

    result = node(state)

    assert isinstance(result["critical_phases"], list)
    assert isinstance(result["low_impact_phases"], list)
    assert isinstance(result["optimization_opportunities"], list)
