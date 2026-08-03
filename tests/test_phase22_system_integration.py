"""Tests for Phase 22: System Integration & Physical Control."""
import pytest
from agents.phase22_system_integration import (
    make_device_discovery_node,
    make_smart_home_control_node,
    make_iot_integration_node,
    make_physical_integration_summary_node,
)
from agents.state import FullAgentState


def fake_llm(prompt: str) -> str:
    """Fake LLM for deterministic testing."""
    if "Discover smart devices" in prompt:
        return """DEVICES: [smart lights, thermostat, security system, door locks, camera]
CAPABILITIES: [lighting control, temperature management, surveillance, access control]
REGISTRY: [5 devices registered and configured]
READINESS: 0.88
CONFIDENCE: 0.91"""
    elif "Manage smart home" in prompt:
        return """CONTROLS: [lighting automated, temperature optimized, security armed]
AUTOMATIONS: [morning routine, evening routine, away mode, sleep mode]
COMFORT: 0.85
SUGGESTIONS: [add occupancy sensors, optimize HVAC schedule, integrate weather data]
CONFIDENCE: 0.89"""
    elif "Integrate IoT systems" in prompt:
        return """WEARABLES: [smartwatch, fitness tracker, sleep monitor]
SENSORS: [temperature, humidity, motion, light level, air quality]
HEALTH: [heart rate monitoring, sleep quality tracking, activity levels]
ACTIVITY: [movement tracking, location history, routine patterns]
AWARENESS: 0.79
CONFIDENCE: 0.86"""
    return ""


def test_device_discovery_node():
    """Test Phase 22a device discovery node."""
    node = make_device_discovery_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Set up smart home",
        "environment_name": "home",
        "user_profile": {"location": "living room"},
    }

    result = node(state)

    assert len(result["discovered_devices"]) > 0
    assert "lights" in str(result["discovered_devices"]).lower() or "device" in str(result["discovered_devices"]).lower()
    assert result["integration_readiness"] > 0.8
    assert result["discovery_confidence"] > 0.9


def test_device_discovery_node_no_environment():
    """Test device discovery with no environment specified."""
    node = make_device_discovery_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Discover devices",
        "environment_name": "",
    }

    result = node(state)

    assert result["discovered_devices"] == []
    assert result["device_registry"] == {}
    assert result["discovery_confidence"] == 0.0


def test_smart_home_control_node():
    """Test Phase 22b smart home control node."""
    node = make_smart_home_control_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Optimize home",
        "discovered_devices": ["lights", "thermostat", "security"],
        "user_preferences": {"comfort": "high", "energy_saving": "moderate"},
    }

    result = node(state)

    assert len(result["environmental_controls"]) > 0
    assert len(result["active_automations"]) > 0
    assert result["comfort_level"] > 0.7
    assert result["smart_home_confidence"] > 0.85


def test_smart_home_control_node_no_devices():
    """Test smart home control with no devices."""
    node = make_smart_home_control_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No devices",
        "discovered_devices": [],
    }

    result = node(state)

    assert result["environmental_controls"] == []
    assert result["active_automations"] == []
    assert result["smart_home_confidence"] == 0.0


def test_iot_integration_node():
    """Test Phase 22c IoT integration node."""
    node = make_iot_integration_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Integrate wearables",
        "discovered_devices": ["smartwatch", "fitness_tracker"],
        "user_profile": {"name": "Alice"},
    }

    result = node(state)

    assert len(result["connected_wearables"]) > 0
    assert len(result["sensor_streams"]) > 0
    assert isinstance(result["health_metrics"], dict)
    assert result["iot_awareness_level"] > 0.7
    assert result["iot_integration_confidence"] > 0.8


def test_iot_integration_node_no_devices():
    """Test IoT integration with no devices."""
    node = make_iot_integration_node(fake_llm)
    state: FullAgentState = {
        "input_text": "No wearables",
        "discovered_devices": [],
    }

    result = node(state)

    assert result["connected_wearables"] == []
    assert result["sensor_streams"] == []
    assert result["iot_integration_confidence"] == 0.0


def test_physical_integration_summary_node():
    """Test Phase 22d physical integration summary node."""
    node = make_physical_integration_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Summarize integration",
        "discovered_devices": ["lights", "thermostat", "security"],
        "connected_wearables": ["smartwatch"],
        "comfort_level": 0.85,
        "active_automations": ["morning_routine", "away_mode"],
        "health_metrics": {"heart_rate": "normal"},
    }

    result = node(state)

    assert result["physical_integration_ready"] is True
    assert result["environmental_control_active"] is True
    assert result["iot_integration_complete"] is True
    assert "System Integration" in result["phase22_summary"]
    assert "Physical Control" in result["phase22_summary"]


def test_physical_integration_summary_node_minimal():
    """Test physical integration summary with minimal data."""
    node = make_physical_integration_summary_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Minimal",
    }

    result = node(state)

    assert result["physical_integration_ready"] is True
    assert result["environmental_control_active"] is True
    assert result["iot_integration_complete"] is True
    assert "System Integration" in result["phase22_summary"]


def test_device_discovery_parsing():
    """Test device discovery response parsing."""
    node = make_device_discovery_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Test parsing",
        "environment_name": "test_env",
    }

    result = node(state)

    assert isinstance(result["discovered_devices"], list)
    assert isinstance(result["device_capabilities"], dict)
    assert isinstance(result["integration_readiness"], float)


def test_smart_home_controls_types():
    """Test smart home control field types."""
    node = make_smart_home_control_node(fake_llm)
    state: FullAgentState = {
        "input_text": "Type test",
        "discovered_devices": ["device1"],
    }

    result = node(state)

    assert isinstance(result["environmental_controls"], list)
    assert isinstance(result["active_automations"], list)
    assert isinstance(result["comfort_level"], float)
    assert isinstance(result["suggested_adjustments"], list)


def test_full_system_integration_pipeline():
    """Test full system integration pipeline."""
    discovery_node = make_device_discovery_node(fake_llm)
    control_node = make_smart_home_control_node(fake_llm)
    iot_node = make_iot_integration_node(fake_llm)
    summary_node = make_physical_integration_summary_node(fake_llm)

    state: FullAgentState = {
        "input_text": "Full integration test",
        "environment_name": "smart_home",
        "user_profile": {"name": "User", "location": "home"},
        "user_preferences": {"comfort": "high"},
    }

    # Step 1: Discover devices
    state = discovery_node(state)
    assert len(state["discovered_devices"]) > 0

    # Step 2: Control smart home
    state = control_node(state)
    assert state["comfort_level"] > 0.0

    # Step 3: Integrate IoT
    state = iot_node(state)
    assert isinstance(state["health_metrics"], dict)

    # Step 4: Generate summary
    state = summary_node(state)
    assert "phase22_summary" in state
    assert len(state["phase22_summary"]) > 0
    assert state["physical_integration_ready"] is True
