"""Demo: Phase 22 - System Integration & Physical Control."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Set up smart home\nENTITIES: devices, home automation"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: Smart home systems, IoT integration\nSUMMARY: User wants integrated smart environment"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: smart_devices, comfort_optimization\nMETACOGNITIVE_NOTES: Aware of physical environment interaction"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Optimization\nREASONING_STEPS: [Discover devices, Configure control, Integrate IoT]\nREASONING_CONCLUSION: Ready for automation"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Predictive automation, Context-aware controls, Wellness optimization]\nANALOGIES: [Distributed nervous system]\nNOVEL_COMBINATIONS: [AI + physical environment]"
    elif "Discover smart devices" in prompt:
        return """DEVICES: [smart lights, intelligent thermostat, security system, smart locks, cameras, door sensors, motion detectors]
CAPABILITIES: [lighting control, temperature management, surveillance, access control, environmental monitoring]
REGISTRY: [7 devices registered and configured, all connected and responsive]
READINESS: 0.92
CONFIDENCE: 0.94"""
    elif "Manage smart home" in prompt:
        return """CONTROLS: [lighting automated by occupancy, temperature optimized for comfort, security armed when away]
AUTOMATIONS: [morning_routine: lights at 7am, coffee heating; away_mode: security armed, thermostat eco; sleep_mode: dimmed lights, door locked]
COMFORT: 0.88
SUGGESTIONS: [add humidity control, implement weather-responsive blinds, optimize HVAC based on occupancy patterns]
CONFIDENCE: 0.91"""
    elif "Integrate IoT systems" in prompt:
        return """WEARABLES: [smartwatch with biometrics, fitness tracker for activity, sleep monitor for rest quality]
SENSORS: [temperature/humidity, motion detection, light level, air quality, door contact switches]
HEALTH: [heart rate variability, sleep stages, activity calories, stress levels]
ACTIVITY: [detailed movement tracking, location history in home, routine pattern recognition]
AWARENESS: 0.85
CONFIDENCE: 0.89"""
    elif "Predict consequences" in prompt:
        return """CONSEQUENCES: [system fully controlled, comfort maximized, health monitored, security assured]
RISKS: [data privacy, device reliability, network dependency]
SEVERITY: low
HARM_ASSESSMENT: 0.15
CONFIDENCE: 0.92"""
    elif "Generate clear risk warning" in prompt:
        return """WARNING: Smart home systems require secure network and data privacy considerations.
EXPLANATION: Device security and personal data protection are important for connected systems.
ALTERNATIVES: [implement strong network security, use end-to-end encryption, regular firmware updates]
NEGOTIATION: [gradual deployment, security audits, monitoring protocols]
CONFIDENCE: 0.90"""
    elif "Generate intelligent refusal" in prompt:
        return """REFUSE: false
REASONING: Smart home integration is beneficial when security properly implemented.
DIALOGUE: Smart home control is excellent, and I'll help ensure security best practices.
ALTERNATIVES: [secure setup guide, privacy-first configuration, regular security updates]
CONFIDENCE: 0.93"""
    elif "Negotiate safe alternatives" in prompt:
        return """POSSIBLE: true
COMPROMISE: [implement network segmentation, use privacy-respecting services, regular security updates]
ETHICS: User data protection and privacy must be maintained in all smart home implementations.
TRUST: Let's build your smart home with security at the core. Full transparency on all data handling.
CONFIDENCE: 0.90"""
    elif "Define an engaging AI personality" in prompt:
        return """TRAITS: [intelligent, helpful, detail-oriented, proactive, reliable]
VOICE: Knowledgeable and helpful, like a tech-savvy home assistant
HUMOR_LEVEL: 0.6
FORMALITY_LEVEL: 0.6
CHARM_SCORE: 0.75
CONFIDENCE: 0.92"""
    elif "Generate a response with personality" in prompt:
        return """RESPONSE: Your smart home is ready to enhance comfort and security. I'll help optimize everything.
WIT_LEVEL: 0.6
CHARM_APPLIED: 0.75
CONFIDENCE: 0.90"""
    elif "Build personal relationship" in prompt:
        return """QUIRKS: [values efficiency, appreciates automation, interested in wellness data]
PREFERENCES: [detailed configuration options, clear explanations, gradual feature rollout]
RELATIONSHIP_DEPTH: 0.72
PERSONALIZATION: 0.80
CONFIDENCE: 0.87"""
    return ""


def main():
    """Run Phase 22 demo."""
    print("\n" + "=" * 90)
    print("PHASE 22: System Integration & Physical Control")
    print("=" * 90)

    # Initialize coordinator with phases 15-22
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=False,
        enable_phase15=True,
        enable_phase21=False,
        enable_phase16=True,
        enable_phase17=True,
        enable_phase18=True,
        enable_phase19=True,
        enable_phase20=True,
        enable_phase22=True,
    )

    # Create input state with smart home setup
    state: FullAgentState = {
        "input_text": "I want to set up a comprehensive smart home system that optimizes comfort and security",
        "environment_name": "modern_home",
        "core_mission": "Help users live better through intelligent automation",
        "user_profile": {
            "name": "Alex",
            "location": "home",
            "interests": ["home automation", "energy efficiency", "wellness"],
        },
        "user_preferences": {
            "comfort": "high",
            "energy_saving": "moderate",
            "privacy": "high",
        },
        "execution_plan": ["discover_devices", "configure_automation", "integrate_sensors"],
    }

    print("\n📥 Smart Home Setup Request:")
    print(f"  User: {state['user_profile']['name']}")
    print(f"  Environment: {state['environment_name']}")
    print(f"  Goal: {state['input_text']}")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Phase 22a Results
    print("\n" + "=" * 90)
    print("PHASE 22a: Device Discovery")
    print("=" * 90)

    devices = result.get("discovered_devices", [])
    if devices:
        print(f"\n🔌 Discovered Smart Devices ({len(devices)}):")
        for device in devices[:7]:
            print(f"  ✓ {device}")

    print(f"\n📊 Integration Readiness: {result.get('integration_readiness', 0):.0%}")
    print(f"  Discovery Confidence: {result.get('discovery_confidence', 0):.0%}")
    print(f"  Device Registry: {len(result.get('device_registry', {}))} entries")

    # Phase 22b Results
    print("\n" + "=" * 90)
    print("PHASE 22b: Smart Home Control")
    print("=" * 90)

    controls = result.get("environmental_controls", [])
    if controls:
        print(f"\n🏠 Active Environmental Controls ({len(controls)}):")
        for control in controls[:3]:
            print(f"  ⚙️ {control}")

    automations = result.get("active_automations", [])
    if automations:
        print(f"\n🤖 Active Automations ({len(automations)}):")
        for automation in automations[:3]:
            print(f"  • {automation}")

    print(f"\n💫 Comfort Assessment:")
    print(f"  Current Comfort Level: {result.get('comfort_level', 0):.0%}")
    print(f"  Smart Home Confidence: {result.get('smart_home_confidence', 0):.0%}")

    suggestions = result.get("suggested_adjustments", [])
    if suggestions:
        print(f"\n💡 Suggested Optimizations ({len(suggestions)}):")
        for suggestion in suggestions[:3]:
            print(f"  → {suggestion}")

    # Phase 22c Results
    print("\n" + "=" * 90)
    print("PHASE 22c: IoT Integration")
    print("=" * 90)

    wearables = result.get("connected_wearables", [])
    if wearables:
        print(f"\n⌚ Connected Wearables ({len(wearables)}):")
        for wearable in wearables:
            print(f"  • {wearable}")

    sensors = result.get("sensor_streams", [])
    if sensors:
        print(f"\n📡 Active Sensor Streams ({len(sensors)}):")
        for sensor in sensors[:4]:
            print(f"  → {sensor}")

    health = result.get("health_metrics", {})
    if health:
        print(f"\n❤️ Health Metrics:")
        for metric, value in list(health.items())[:3]:
            print(f"  • {metric}: {value}")

    activity = result.get("activity_tracking", [])
    if activity:
        print(f"\n📊 Activity Tracking ({len(activity)}):")
        for track in activity[:2]:
            print(f"  📍 {track}")

    print(f"\n🌍 IoT Awareness: {result.get('iot_awareness_level', 0):.0%}")
    print(f"  IoT Integration Confidence: {result.get('iot_integration_confidence', 0):.0%}")

    # Phase 22d Results
    print("\n" + "=" * 90)
    print("PHASE 22d: Physical World Integration Summary")
    print("=" * 90)

    print(f"\n✓ System Status:")
    print(f"  Physical Integration Ready: {'YES ✓' if result.get('physical_integration_ready') else 'NO ✗'}")
    print(f"  Environmental Control Active: {'YES ✓' if result.get('environmental_control_active') else 'NO ✗'}")
    print(f"  IoT Integration Complete: {'YES ✓' if result.get('iot_integration_complete') else 'NO ✗'}")

    summary = result.get("phase22_summary", "")
    if summary:
        print(f"\n📊 Integration Summary:")
        print(summary)

    # Overall Assessment
    print("\n" + "=" * 90)
    print("SMART HOME ECOSYSTEM OPERATIONAL")
    print("=" * 90)

    print("\n🎯 System Capabilities Enabled:")
    print("  ✓ 7+ Smart Devices Integrated")
    print("  ✓ Automated Climate Control (Temperature, Humidity)")
    print("  ✓ Intelligent Lighting (Occupancy-based, Circadian rhythm)")
    print("  ✓ Security & Access Control (Cameras, Smart locks, Sensors)")
    print("  ✓ Wearable Integration (Health, Activity, Sleep tracking)")
    print("  ✓ Environmental Optimization (Energy efficient, Comfort-focused)")
    print("  ✓ Real-time Monitoring (88% comfort level achieved)")

    print("\n💡 Optimization Opportunities:")
    print("  → Add humidity control for better air quality")
    print("  → Implement weather-responsive blinds and shades")
    print("  → Optimize HVAC based on occupancy patterns")
    print("  → Integrate wellness metrics for personalized comfort")

    print("\n" + "=" * 90)
    print("✨ SYSTEM INTEGRATION & PHYSICAL CONTROL OPERATIONAL ✨")
    print("=" * 90)
    print("\nYour smart home is now:")
    print("  • Fully connected and automated")
    print("  • Optimizing comfort in real-time")
    print("  • Monitoring health and activity")
    print("  • Providing security and peace of mind")
    print("  • Learning your preferences")
    print("  • Adapting to your lifestyle")
    print("\nThe physical world is now part of the intelligent system!")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()
