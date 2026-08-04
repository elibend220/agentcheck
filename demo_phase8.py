#!/usr/bin/env python3
"""
Demonstration of Phase 8: Error Recovery & Intelligent Retry.

Shows full 1-8 pipeline with error detection, recovery planning, and intelligent retry.
"""

import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager, ExecutionMemory


class DemoLLM:
    """LLM for demonstration with intelligent error recovery responses."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Phase 1: NLP
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Calculate sum and transform to text
ENTITIES: numbers (5, 3), transformation
SUMMARY: Add two numbers and convert result to uppercase"""

        # Phase 2: Knowledge
        if "knowledge" in prompt_lower or "retrieve" in prompt_lower:
            return """KNOWLEDGE_POINTS: arithmetic operations, text transformation
KNOWLEDGE_SUMMARY: Math operations produce reliable results; text transformation always succeeds
CONFIDENCE: 0.85"""

        # Phase 3a: Consciousness (Attention)
        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: mathematical accuracy, tool reliability
METACOGNITIVE_NOTES: Confident in math but uncertain about text processing chains
CONFIDENCE: 0.75"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt_lower and ("causal" in prompt_lower or "analyze" in prompt_lower):
            return """REASONING_TYPE: logical
CAUSAL: Using math tools produces numerical results; text tools transform strings
LOGICAL: Sequential tool execution works best
PROBABILISTIC: 80% chance of success with proper tool selection
COMMON_SENSE: Start with math, follow with text transformation
CONCLUSION: Proceed with selected tool sequence"""

        # Phase 3c: Creativity
        if "creative" in prompt_lower or "novelty" in prompt_lower:
            return """CREATIVE_IDEAS: Chain tools sequentially, parallel text operations
ANALOGIES: Similar to data pipelines and ETL processes
CONCEPTUAL_BLEND: Numerical processing followed by text formatting
NOVELTY_SCORE: 72"""

        # Phase 4a: Tool Selection
        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Math for calculation, text for formatting
CONFIDENCE: 0.9"""

        # Phase 4b: Parameter Binding
        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 5\nb: 3"

        # Phase 4c: Tool Verification
        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.92
CONCERNS: none
REASONING: Math result verified, text transformation successful"""

        # Phase 5: Quantum Optimization
        if "quantum" in prompt_lower or "superposition" in prompt_lower:
            return """QUANTUM_STATE: superposition of 4 tool combinations
ENTANGLEMENT: math.add and text.uppercase show high coupling
TUNNELING: Alternative path via text.split identified
AMPLITUDES: {"math.add": 0.85, "text.uppercase": 0.80}
CONFIDENCE: 0.88"""

        # Phase 6: Learning & Feedback
        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool sequence execution verified
LESSON 2: Math operations most reliable
LESSON 3: Text formatting effective after math"""

        # Phase 6: Improvement Suggestions
        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Increase timeout for complex operations
SUGGESTION 2: Validate intermediate results
SUGGESTION 3: Consider alternative text processing approaches"""

        # Phase 7: Memory Retrieval & Synthesis
        if "similar" in prompt_lower and ("past" in prompt_lower or "execution" in prompt_lower):
            return """INSIGHT 1: Tool sequence worked in similar past tasks
INSIGHT 2: Sequential math→text approach is most effective
CONFIDENCE: 0.85
RECOMMENDED_APPROACH: Use math.add followed by text.uppercase"""

        # Phase 8: Error Detection & Analysis
        if "analyze" in prompt_lower and ("failure" in prompt_lower or "execution" in prompt_lower):
            return """ROOT_CAUSE: Tool incompatibility in sequence
RECOVERY_OPTIONS: alternative_sequence, retry_with_validation, adjust_timeout
RISK_LEVEL: low
RECOMMENDED_ACTION: Retry with enhanced validation and alternative tool sequence"""

        # Phase 8: Retry Planning
        if "retry" in prompt_lower or "recovery" in prompt_lower:
            return """ALTERNATIVE_TOOLS: text.split, math.multiply
PARAMETER_ADJUSTMENTS: increase timeout to 10s, add validation
EXECUTION_SEQUENCE: math.add → text.uppercase → validation
REASONING: This combination succeeded in 92% of similar past tasks
CONFIDENCE: 0.88"""

        # Phase 8: Retry Evaluation
        if "evaluate" in prompt_lower and "retry" in prompt_lower:
            return """OUTCOME: success
IMPROVEMENTS: Better error handling, more robust execution, faster performance
CONFIDENCE: 0.91
EXPLANATION: Enhanced validation and alternative sequence resolved original failure"""

        return "DEFAULT: continue processing"


def main():
    """Run full Phase 1-8 demonstration with error recovery."""
    print("=" * 80)
    print("PHASE 8: ERROR RECOVERY & INTELLIGENT RETRY - FULL PIPELINE DEMONSTRATION")
    print("=" * 80)

    # Create memory manager for persistent learning
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        memory_path = f.name

    memory_manager = MemoryManager(memory_path)

    # Pre-populate memory with successful execution history
    print("\n[Memory Setup] Adding historical successful execution...")
    memory_manager.add_memory(ExecutionMemory(
        input_text="Add numbers and transform to text format",
        execution_outcome="success",
        lessons_learned=[
            "Sequential math→text approach is effective",
            "Proper parameter validation prevents failures",
            "Alternative tool combinations provide robustness",
        ],
        tool_performance_scores={
            "math.add": 0.95,
            "text.uppercase": 0.92,
            "text.split": 0.88,
        },
        effective_tools=["math.add", "text.uppercase"],
        improvement_suggestions=[
            "Add error handling between tool calls",
            "Implement timeout protection",
            "Validate intermediate results",
        ],
        learning_metrics={
            "success_rate": 0.95,
            "avg_execution_time": 0.45,
            "reliability": 0.92,
        },
    ))

    # Create coordinator with all 8 phases enabled
    print("[Coordinator Setup] Enabling all phases 1-8 with memory manager...")
    llm = DemoLLM()
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
        dry_run_mode=True,
    )

    # Scenario 1: Successful execution through all 8 phases
    print("\n" + "=" * 80)
    print("SCENARIO 1: Successful Execution Path (No Recovery Needed)")
    print("=" * 80)

    initial_state: FullAgentState = {
        "input_text": "Add 5 and 3, then convert result to uppercase",
        "execution_outcome": "success",  # Simulating successful execution
    }

    print(f"\nInput: {initial_state['input_text']}")
    print(f"Initial Outcome: {initial_state.get('execution_outcome', 'unknown')}")

    result1 = coordinator.invoke(initial_state)

    print("\n--- Phase Results ---")
    print(f"Phase 1 (NLP) Intent: {result1.get('intent', 'N/A')}")
    print(f"Phase 3b Reasoning: {result1.get('reasoning_conclusion', 'N/A')[:100]}...")
    print(f"Phase 4 Selected Tools: {', '.join(result1.get('selected_tools', []))}")
    print(f"Phase 6 Outcome: {result1.get('execution_outcome', 'N/A')}")
    print(f"Phase 7 Memory Insights: {result1.get('phase7_recommended_approach', 'N/A')[:80]}...")
    print(f"Phase 8 Recovery Needed: {result1.get('recovery_needed', False)}")

    print("\n--- Phase 8 Summary ---")
    print(result1.get("phase8_summary", "N/A"))

    # Scenario 2: Failed execution with recovery
    print("\n" + "=" * 80)
    print("SCENARIO 2: Failed Execution with Recovery Attempt")
    print("=" * 80)

    initial_state2: FullAgentState = {
        "input_text": "Add numbers and format as text - complex operation",
        "execution_outcome": "failure",  # Simulating failure
        "failure_analysis": {
            "analysis": "Tool incompatibility detected in sequential execution",
            "error": "Tool binding failed at parameter validation stage",
        },
    }

    print(f"\nInput: {initial_state2['input_text']}")
    print(f"Initial Outcome: {initial_state2.get('execution_outcome', 'unknown')}")
    print(f"Failure Analysis: {initial_state2['failure_analysis']['analysis']}")

    result2 = coordinator.invoke(initial_state2)

    print("\n--- Phase Results ---")
    print(f"Phase 1 Intent: {result2.get('intent', 'N/A')}")
    print(f"Phase 4 Selected Tools: {', '.join(result2.get('selected_tools', []))}")
    print(f"Phase 6 Execution Outcome: {result2.get('execution_outcome', 'N/A')}")
    print(f"Phase 7 Similar Past Executions: {result2.get('similar_past_executions', 0)}")
    print(f"Phase 8 Recovery Needed: {result2.get('recovery_needed', False)}")
    print(f"Phase 8 Recovery Strategy: {result2.get('recovery_strategy', 'N/A')}")

    if result2.get("retry_attempted"):
        print(f"Phase 8 Retry Attempted: YES")
        retry_plan = result2.get("retry_plan", {})
        print(f"  Alternative Tools: {', '.join(retry_plan.get('alternative_tools', []))}")
        print(f"  Confidence: {retry_plan.get('confidence', 0):.2f}")
    else:
        print(f"Phase 8 Retry Attempted: NO")

    if result2.get("recovery_executed"):
        print(f"\nPhase 8 Recovery Execution:")
        print(f"  Retry Outcome: {result2.get('retry_outcome', 'N/A')}")
        print(f"  Success: {'✓ YES' if result2.get('retry_success') else '✗ NO'}")
        print(f"  Confidence: {result2.get('recovery_confidence', 0):.2f}")

    print("\n--- Phase 8 Summary ---")
    print(result2.get("phase8_summary", "N/A"))

    # Scenario 3: Partial outcome requiring enhancement
    print("\n" + "=" * 80)
    print("SCENARIO 3: Partial Outcome with Reasoning Enhancement")
    print("=" * 80)

    initial_state3: FullAgentState = {
        "input_text": "Complex multi-step text and number transformation",
        "execution_outcome": "partial",  # Simulating partial completion
    }

    print(f"\nInput: {initial_state3['input_text']}")
    print(f"Initial Outcome: {initial_state3.get('execution_outcome', 'unknown')}")

    result3 = coordinator.invoke(initial_state3)

    print("\n--- Phase Results ---")
    print(f"Phase 1 Intent: {result3.get('intent', 'N/A')}")
    print(f"Phase 3b Reasoning: {result3.get('reasoning_conclusion', 'N/A')[:100]}...")
    print(f"Phase 6 Outcome: {result3.get('execution_outcome', 'N/A')}")
    print(f"Phase 8 Recovery Needed: {result3.get('recovery_needed', False)}")
    print(f"Phase 8 Recovery Strategy: {result3.get('recovery_strategy', 'N/A')}")

    print("\n--- Phase 8 Summary ---")
    print(result3.get("phase8_summary", "N/A"))

    # Summary statistics
    print("\n" + "=" * 80)
    print("DEMONSTRATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal LLM Calls Across 3 Scenarios: {llm.call_count}")
    print(f"Memory File Location: {memory_path}")
    print(f"\nKey Achievements:")
    print("  ✓ Phase 1-3: NLP, Knowledge, Consciousness & Reasoning extracted")
    print("  ✓ Phase 4: Tool selection and execution orchestrated")
    print("  ✓ Phase 5: Quantum optimization computed tool superposition")
    print("  ✓ Phase 6: Learning feedback analyzed execution outcome")
    print("  ✓ Phase 7: Memory persistence and historical retrieval integrated")
    print("  ✓ Phase 8: Error detection and intelligent retry attempted recovery")
    print("\nPhase 8 Capabilities:")
    print("  • Error Detection: Identifies failures, partial outcomes")
    print("  • Strategy Determination: Selects recovery approach (alternative tools, parameters, resources)")
    print("  • Historical Integration: Uses Phase 7 memory for past successful patterns")
    print("  • Retry Planning: Generates detailed recovery plans with LLM guidance")
    print("  • Recovery Execution: Simulates retry with adapted strategies")
    print("  • Comprehensive Reporting: Summarizes recovery attempts and outcomes")

    # Cleanup
    import os
    if os.path.exists(memory_path):
        os.remove(memory_path)

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
