#!/usr/bin/env python3
"""
Demonstration of Phase 9: Explainability & Interpretability.

Shows full 1-9 pipeline with reasoning traces, confidence justification, and decision auditing.
"""

import tempfile
import json
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class DemoLLMPhase9:
    """LLM for demonstration with explainability-focused responses."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Phase 1: NLP
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Analyze market trends and provide recommendations
ENTITIES: market, trends, recommendations
SUMMARY: Task requires market analysis and strategic insights"""

        # Phase 2: Knowledge
        if "knowledge" in prompt_lower or "retrieve" in prompt_lower:
            return """KNOWLEDGE_POINTS: market analysis frameworks, trend analysis, strategic recommendations
KNOWLEDGE_SUMMARY: Deep knowledge available on market dynamics and analysis techniques"""

        # Phase 3a: Consciousness
        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: accuracy in market analysis, relevance of trends
METACOGNITIVE_NOTES: High confidence in analytical capabilities, awareness of market complexity"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: analytical
CAUSAL: Market forces drive trend changes
LOGICAL: Trend analysis follows established frameworks
PROBABILISTIC: 85% confidence in trend identification
CONCLUSION: Proceed with comprehensive analysis"""

        # Phase 3c: Creativity
        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Cross-domain trend analysis, pattern synthesis
ANALOGIES: Market analysis similar to scientific hypothesis testing
NOVELTY_SCORE: 78"""

        # Phase 4a: Tool Selection
        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: data.aggregate, text.summarize, math.calculate
REASONING: Aggregate data, summarize findings, calculate metrics
CONFIDENCE: 0.92"""

        # Phase 4b: Parameter Binding
        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "threshold: 0.75\nperiod: 12"

        # Phase 4c: Verification
        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.93
CONCERNS: none
REASONING: All validations passed"""

        # Phase 5: Quantum
        if "quantum" in prompt_lower:
            return """QUANTUM_STATE: superposition of 3 analysis approaches
AMPLITUDES: {"data.aggregate": 0.92, "text.summarize": 0.88}
CONFIDENCE: 0.90"""

        # Phase 6: Learning
        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Data aggregation critical for trend identification
LESSON 2: Text summarization reveals key insights
LESSON 3: Quantitative metrics validate findings"""

        # Phase 7: Memory
        if "similar" in prompt_lower and ("past" in prompt_lower or "execution" in prompt_lower):
            return """INSIGHT 1: Similar analyses performed successfully
INSIGHT 2: Cross-domain approach most effective
CONFIDENCE: 0.87
RECOMMENDED_APPROACH: Multi-faceted analysis combining data and text"""

        # Phase 8: Error Recovery
        if "analyze" in prompt_lower and ("failure" in prompt_lower or "execution" in prompt_lower):
            return """ROOT_CAUSE: Tool output inconsistency
RECOVERY_OPTIONS: retry_with_validation, alternative_approach
RISK_LEVEL: low
RECOMMENDED_ACTION: Validate and retry"""

        # Phase 8: Retry Planning
        if "retry" in prompt_lower or "recovery" in prompt_lower:
            return """ALTERNATIVE_TOOLS: data.filter, text.extract
PARAMETER_ADJUSTMENTS: Lower threshold to 0.70
REASONING: More inclusive analysis captures edge cases
CONFIDENCE: 0.89"""

        # Phase 9a: Reasoning Trace
        if "reasoning trace" in prompt_lower or ("generate" in prompt_lower and "trace" in prompt_lower):
            return """SUMMARY: Comprehensive market analysis reasoning trace generated
REASONING: Multi-phase analytical approach applied systematically
ALTERNATIVES: Single-phase analysis considered and rejected
CONFIDENCE_FACTORS: Strong data validation, established frameworks"""

        # Phase 9b: Confidence Justification
        if "explain why" in prompt_lower or ("confidence" in prompt_lower and "explain" in prompt_lower):
            return """REASONING: Confidence justified by multiple validation layers
SUPPORTING_EVIDENCE: Data consistency, framework adherence, expert patterns
LIMITING_FACTORS: Market volatility, external uncertainty
OVERALL_ASSESSMENT: Confidence well-founded despite inherent complexity"""

        return "DEFAULT: processing complete"


def main():
    """Run full Phase 1-9 demonstration with explainability."""
    print("=" * 90)
    print("PHASE 9: EXPLAINABILITY & INTERPRETABILITY - FULL 1-9 PIPELINE DEMONSTRATION")
    print("=" * 90)

    # Create memory manager
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        memory_path = f.name

    memory_manager = MemoryManager(memory_path)

    # Create coordinator with all 9 phases enabled
    print("\n[Setup] Enabling all phases 1-9 with full explainability...")
    llm = DemoLLMPhase9()
    registry = create_builtin_registry()
    safety_validator = SafetyValidator()

    coordinator = AgentCoordinator(
        llm=llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=memory_manager,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        dry_run_mode=True,
    )

    # Execute analysis task
    print("\n" + "=" * 90)
    print("FULL 1-9 PIPELINE EXECUTION: Market Analysis with Complete Explainability")
    print("=" * 90)

    initial_state: FullAgentState = {
        "input_text": "Analyze current market trends and provide strategic recommendations for Q4 2026",
        "tool_selection_confidence": 0.92,
        "outcome_confidence": 0.88,
    }

    print(f"\nInput Task: {initial_state['input_text']}")
    print("\nExecuting all 9 phases...")

    result = coordinator.invoke(initial_state)

    # Display Phase Results
    print("\n" + "=" * 90)
    print("PHASE RESULTS")
    print("=" * 90)

    print("\n[Phase 1-3] NLP, Knowledge, Consciousness & Reasoning:")
    print(f"  Intent: {result.get('intent', 'N/A')[:60]}...")
    print(f"  Reasoning: {result.get('reasoning_conclusion', 'N/A')[:60]}...")
    print(f"  Creative Ideas: {len(result.get('creative_ideas', []))} ideas generated")

    print("\n[Phase 4] Tool Selection & Execution:")
    print(f"  Selected Tools: {', '.join(result.get('selected_tools', []))}")
    print(f"  Selection Confidence: {result.get('tool_selection_confidence', 0):.2%}")

    print("\n[Phase 5] Quantum Optimization:")
    print(f"  Quantum State Created: {result.get('quantum_state_created', False)}")
    print(f"  Optimized Tools: {len(result.get('quantum_optimized_tools', []))} tools")

    print("\n[Phase 6] Learning & Feedback:")
    print(f"  Execution Outcome: {result.get('execution_outcome', 'N/A')}")
    print(f"  Lessons Learned: {len(result.get('lessons_learned', []))} lessons")

    print("\n[Phase 7] Memory & Knowledge Integration:")
    print(f"  Memory Persisted: {result.get('memory_persisted', False)}")
    print(f"  Similar Past Executions: {result.get('similar_past_executions', 0)}")

    print("\n[Phase 8] Error Recovery:")
    print(f"  Recovery Needed: {result.get('recovery_needed', False)}")
    if result.get("recovery_needed"):
        print(f"  Recovery Strategy: {result.get('recovery_strategy', 'N/A')}")

    # Display Explainability Results
    print("\n" + "=" * 90)
    print("PHASE 9: EXPLAINABILITY & INTERPRETABILITY RESULTS")
    print("=" * 90)

    # Reasoning Traces
    traces = result.get("reasoning_traces", {})
    print(f"\n[9a] Reasoning Traces Generated: {len(traces)}")
    for phase_name in sorted(list(traces.keys())[:3]):
        trace = traces[phase_name]
        print(f"  ✓ {phase_name}: {trace.get('summary', 'N/A')[:55]}...")

    # Confidence Justifications
    justifications = result.get("confidence_justifications", {})
    print(f"\n[9b] Confidence Justifications: {len(justifications)}")
    for key, just in list(justifications.items())[:3]:
        print(f"  ✓ {key}: {just.get('reasoning', 'N/A')[:50]}...")

    # Decision Audit Log
    audit_log = result.get("decision_audit_log", [])
    print(f"\n[9c] Decision Audit Trail: {len(audit_log)} decisions logged")
    for entry in audit_log[:3]:
        confidence = entry.get('confidence', 0)
        print(f"  ✓ {entry['decision_type']}: {str(entry.get('decision', 'N/A'))[:40]}... (confidence: {confidence:.2f})")

    # Explainability Metrics
    print(f"\n[9d] Explainability Metrics:")
    print(f"  Overall System Confidence: {result.get('overall_system_confidence', 0):.2%}")
    print(f"  Explainability Score: {result.get('explainability_score', 0):.2%}")
    print(f"  Audit Log Entries: {len(audit_log)}")
    print(f"  Reasoning Traces: {len(traces)}")

    # Full Phase 9 Summary
    print(f"\n[Phase 9 Summary]")
    print(result.get("phase9_summary", "N/A"))

    # Statistics
    print("\n" + "=" * 90)
    print("EXECUTION STATISTICS")
    print("=" * 90)
    print(f"Total LLM Calls: {llm.call_count}")
    print(f"Total Phases Executed: 9")
    print(f"Total Phases with Reasoning Traces: {len(traces)}")
    print(f"Audit Trail Entries: {len(audit_log)}")
    print(f"System Transparency Level: {result.get('explainability_score', 0):.1%}")

    # Key Insights
    print("\n" + "=" * 90)
    print("KEY EXPLAINABILITY INSIGHTS")
    print("=" * 90)
    print("""
✓ Phase 9 provides complete transparency into all pipeline decisions
✓ Reasoning traces explain each phase's logic and alternatives considered
✓ Confidence justifications validate each high-confidence decision
✓ Decision audit log creates auditable record of all key choices
✓ Explainability score quantifies system interpretability

This completes the 9-phase AGI framework:
  1. NLP Processing → 2. Knowledge Retrieval → 3. Consciousness & Reasoning → 4. Creativity
  5. Tool Selection & Execution → 6. Quantum Optimization → 7. Learning & Feedback
  8. Memory & Knowledge Integration → 9. Error Recovery → 10. Explainability & Transparency
    """)

    # Cleanup
    import os
    if os.path.exists(memory_path):
        os.remove(memory_path)

    print("\n" + "=" * 90)
    print("DEMONSTRATION COMPLETE - 9-PHASE AGI PIPELINE FULLY OPERATIONAL")
    print("=" * 90)


if __name__ == "__main__":
    main()
