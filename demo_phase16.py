"""Demo: Phase 16 - System Engineering & Self-Optimization."""
from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.schema import ToolRegistry


def fake_llm(prompt: str) -> str:
    """Fake LLM returning deterministic responses."""
    if "intent" in prompt.lower():
        return "INTENT: Optimize system performance\nENTITIES: system, performance, optimization"
    elif "knowledge" in prompt.lower():
        return "RELEVANT_KNOWLEDGE: System optimization, performance tuning\nSUMMARY: Self-optimization improves efficiency"
    elif "consciousness" in prompt.lower():
        return "ATTENTION_FOCUS: system_performance, efficiency, bottlenecks\nMETACOGNITIVE_NOTES: Meta-analysis enables self-improvement"
    elif "reasoning" in prompt.lower():
        return "REASONING_TYPE: Analytical\nREASONING_STEPS: [Analyze metrics, Identify bottlenecks, Recommend changes, Apply optimizations]\nREASONING_CONCLUSION: System self-optimization works"
    elif "creativity" in prompt.lower():
        return "CREATIVE_IDEAS: [Dynamic phase routing, Adaptive resource allocation]\nANALOGIES: [Evolution, Continuous improvement]\nNOVEL_COMBINATIONS: [ML-based phase ordering]"
    elif "Analyze system performance metrics" in prompt:
        return """PHASE_LATENCIES: [phase1: 45ms, phase4: 150ms, phase6: 85ms, phase14: 120ms]
SUCCESS_RATES: [phase1: 99%, phase4: 90%, phase6: 96%, phase14: 92%]
NODE_EXECUTION_COUNTS: [nlp: 1, tool_selection: 1, learning: 1, streaming: 1]
RESOURCE_USAGE: [memory_mb: 512, cpu_percent: 65]
BOTTLENECK_PHASES: [phase4, phase14]
CONFIDENCE: 0.89"""
    elif "Analyze system architecture" in prompt:
        return """CRITICAL_PHASES: [phase1, phase4, phase6, phase14]
LOW_IMPACT_PHASES: [phase3c_creativity, phase11_personal_assistant]
PHASE_COUPLING: [phase4 depends on phase1, phase6 on phase4, phase14 on phase12]
OPPORTUNITIES: [Reduce phase4 overhead 30%, Optimize phase14 latency 20%, Enable phase16]
CONFIDENCE: 0.87"""
    elif "Generate system optimization recommendations" in prompt:
        return """PHASE_CHANGES: [Optimize phase4 execution path, Improve phase14 event batching]
ROUTING_CHANGES: [Fast-track common sequences, Cache phase results, Parallel phase14 processing]
RESOURCE_ALLOCATION: [Increase phase4 resources to 30%, Reduce phase3 to 5%, Enable phase16 100%]
PRIORITY: [Critical: phase4 optimization, High: phase14 latency, Medium: resource reallocation]
CONFIDENCE: 0.85"""
    elif "Apply system optimizations" in prompt:
        return """APPLIED_CHANGES: [Phase4 execution optimized, Phase14 batching enabled, Resource rebalancing complete]
IMPACT: [Phase4 latency reduced 25%, Phase14 latency reduced 18%, Overall throughput +15%]
READY: true
CONFIDENCE: 0.88"""
    return ""


def main():
    """Run Phase 16 demo."""
    print("\n" + "=" * 80)
    print("PHASE 16: System Engineering & Self-Optimization")
    print("=" * 80)

    # Initialize coordinator with all phases enabled including Phase 16
    coordinator = AgentCoordinator(
        llm=fake_llm,
        tool_registry=ToolRegistry(),
        enable_phase14=True,
        enable_phase15=True,
        enable_phase21=True,
        enable_phase16=True,
    )

    # Create input state
    state: FullAgentState = {
        "input_text": "Analyze system performance and recommend optimizations",
        "execution_history": [
            {"phase": "1", "latency": 45},
            {"phase": "4", "latency": 150},
            {"phase": "6", "latency": 85},
        ] * 5,
    }

    print("\n📥 Input:")
    print(f"  Task: {state['input_text']}")
    print(f"  System History: {len(state['execution_history'])} executions analyzed")

    # Execute pipeline
    result = coordinator.invoke(state)

    # Display results
    print("\n📊 Phase 16a: Metrics Collection")
    print(f"  Metrics Confidence: {result.get('metrics_collection_confidence', 0):.0%}")
    latencies = result.get("phase_latencies", {})
    if latencies:
        print(f"  Latencies: {', '.join([f'{k}: {v:.0f}ms' for k, v in list(latencies.items())[:3]])}")
    bottlenecks = result.get("bottleneck_phases", [])
    if bottlenecks:
        print(f"  Bottlenecks: {', '.join(bottlenecks[:2])}")

    print("\n🔍 Phase 16b: Architecture Analysis")
    print(f"  Analysis Confidence: {result.get('architecture_analysis_confidence', 0):.0%}")
    critical = result.get("critical_phases", [])
    if critical:
        print(f"  Critical Phases: {', '.join(critical[:3])}")
    low_impact = result.get("low_impact_phases", [])
    if low_impact:
        print(f"  Low Impact Phases: {', '.join(low_impact[:2])}")
    opps = result.get("optimization_opportunities", [])
    if opps:
        print(f"  Opportunities ({len(opps)}):")
        for opp in opps[:3]:
            print(f"    • {opp}")

    print("\n💡 Phase 16c: Optimization Recommendations")
    print(f"  Recommendation Confidence: {result.get('optimization_recommendation_confidence', 0):.0%}")
    phase_changes = result.get("recommended_phase_changes", [])
    if phase_changes:
        print(f"  Phase Changes ({len(phase_changes)}):")
        for change in phase_changes[:2]:
            print(f"    → {change}")
    routing_changes = result.get("recommended_routing_changes", [])
    if routing_changes:
        print(f"  Routing Changes ({len(routing_changes)}):")
        for change in routing_changes[:2]:
            print(f"    → {change}")
    priority = result.get("optimization_priority", [])
    if priority:
        print(f"  Priority Order: {' > '.join(priority[:3])}")

    print("\n⚙️  Phase 16d: Adaptive Configuration")
    print(f"  Applied Optimizations: {result.get('optimization_applied', False)}")
    print(f"  Configuration Confidence: {result.get('optimization_applied_confidence', 0):.0%}")
    applied = result.get("applied_optimizations", [])
    if applied:
        print(f"  Changes Applied ({len(applied)}):")
        for change in applied[:3]:
            print(f"    ✓ {change}")

    print("\n📊 Phase 16d: System Engineering Summary")
    print(result.get("phase16_summary", "No summary"))

    print("\n✨ System Optimization Status:")
    print(f"  System Optimized: {result.get('system_optimized', False)}")
    print(f"  Self-Optimization Ready: {result.get('optimization_applied', False)}")
    print(f"  Overall Optimization Confidence: {result.get('optimization_applied_confidence', 0):.0%}")

    print("\n" + "=" * 80)
    print("Demo complete! System engineering and self-optimization operational.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
