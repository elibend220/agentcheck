"""
Full Phase 1-5 AGI Pipeline Demo

Demonstrates the complete integrated reasoning system with:
- Phase 1: NLP (intent, entities, summary)
- Phase 2: Knowledge (semantic retrieval)
- Phase 3a: Consciousness (attention, metacognition)
- Phase 3b: Reasoning (multi-modal analysis)
- Phase 3c: Creativity (novel ideas, analogies)
- Phase 4a: Tool Selection (awareness-justified selection)
- Phase 4b: Tool Execution (safe execution)
- Phase 4c: Tool Verification (result validation)
- Phase 5: Quantum Optimization (superposition → entanglement → tunneling → amplification → annealing)
"""

from agents.coordinator import AgentCoordinator
from agents.state import FullAgentState
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class DemoLLM:
    """Simple deterministic LLM for demonstration."""

    def __call__(self, prompt: str) -> str:
        # Phase 1: NLP
        if "extract intent" in prompt.lower():
            return """INTENT: Calculate sum and convert to uppercase
ENTITIES: number, calculation, text transformation
SUMMARY: Add two numbers and transform the result"""

        # Phase 2: Knowledge
        if "knowledge" in prompt.lower() and "retrieve" in prompt.lower():
            return """KNOWLEDGE_POINTS: Mathematical operations use arithmetic, text transformation is common
KNOWLEDGE_SUMMARY: We know about math operations and text processing"""

        # Phase 3a: Consciousness
        if "attention" in prompt.lower():
            return """ATTENTION_FOCUS: numerical accuracy, result clarity
METACOGNITIVE_NOTES: confident in mathematical operations"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt.lower() and "step" in prompt.lower():
            return """REASONING_TYPE: multi-modal
REASONING_STEPS: 1. Parse input numbers, 2. Perform addition, 3. Format result
REASONING_CONCLUSION: Use math tools for computation, text tools for formatting"""

        # Phase 3c: Creativity
        if "creative" in prompt.lower():
            return """CREATIVE_IDEAS: combine mathematical result with text formatting
ANALOGIES: like a calculator with a printer - compute then output
NOVEL_COMBINATIONS: numerical + textual output"""

        # Phase 4a: Tool Selection
        if "SELECT which tools" in prompt:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Math tool computes sum, text tool formats output
CONFIDENCE: 0.9"""

        # Phase 4b: Parameter Binding
        if "bind" in prompt.lower() or "parameters" in prompt.lower():
            return "a: 5\nb: 3"

        # Phase 4c: Verification
        if "verif" in prompt.lower():
            return """VALID: true
CONFIDENCE: 0.95
CONCERNS: none
REASONING: Math result is correct, formatting is proper"""

        return "CONTINUE: next phase"


def main():
    """Run full Phase 1-5 pipeline demonstration."""
    print("╔" + "="*68 + "╗")
    print("║" + " "*8 + "Full Phase 1-5 AGI Pipeline Demonstration" + " "*21 + "║")
    print("╚" + "="*68 + "╝\n")

    # Setup
    llm = DemoLLM()
    registry = create_builtin_registry()
    safety_validator = SafetyValidator()

    # Create coordinator with all phases enabled
    coordinator = AgentCoordinator(
        llm=llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,  # Enable tool execution
        enable_phase5=True,  # Enable quantum optimization
        dry_run_mode=True,   # Safe demo mode
    )

    # Input
    input_text = "Add 5 and 3, then convert to uppercase"
    print(f"Input: {input_text}\n")

    initial_state: FullAgentState = {
        "input_text": input_text,
    }

    # Execute full pipeline
    print("Running full Phase 1-5 pipeline...\n")
    result = coordinator.invoke(initial_state)

    # Phase 1 Results
    print("="*70)
    print("PHASE 1: Natural Language Processing")
    print("="*70)
    print(f"Intent: {result.get('intent', 'N/A')}")
    print(f"Entities: {', '.join(result.get('entities', []))}")
    print(f"Summary: {result.get('summary', 'N/A')}\n")

    # Phase 2 Results
    print("="*70)
    print("PHASE 2: Knowledge Synthesis")
    print("="*70)
    print(f"Knowledge: {result.get('relevant_knowledge', 'N/A')}\n")

    # Phase 3a Results
    print("="*70)
    print("PHASE 3a: Consciousness (Attention & Metacognition)")
    print("="*70)
    print(f"Attention Focus: {', '.join(result.get('attention_focus', []))}")
    print(f"Metacognition: {result.get('metacognitive_notes', 'N/A')}\n")

    # Phase 3b Results
    print("="*70)
    print("PHASE 3b: Reasoning")
    print("="*70)
    print(f"Reasoning Type: {result.get('reasoning_type', 'N/A')}")
    print(f"Steps: {result.get('reasoning_steps', 'N/A')}")
    print(f"Conclusion: {result.get('reasoning_conclusion', 'N/A')}\n")

    # Phase 3c Results
    print("="*70)
    print("PHASE 3c: Creativity")
    print("="*70)
    print(f"Creative Ideas: {', '.join(result.get('creative_ideas', []))}")
    print(f"Analogies: {', '.join(result.get('analogies', []))}\n")

    # Phase 4 Results
    print("="*70)
    print("PHASE 4: Tool Execution")
    print("="*70)
    print(f"Selected Tools: {', '.join(result.get('selected_tools', []))}")
    print(f"Selection Reasoning: {result.get('tool_selection_reasoning', 'N/A')}")
    print(f"Selection Confidence: {result.get('tool_selection_confidence', 0):.2f}")

    if result.get("tool_execution_results"):
        print("\nExecution Results:")
        for res in result["tool_execution_results"]:
            print(f"  {res.get('tool_id', 'N/A')}: {res.get('output', 'N/A')}")

    if result.get("verified_results"):
        print("\nVerification:")
        for res in result["verified_results"]:
            print(f"  {res.get('tool_id', 'N/A')}: Valid={res.get('is_valid', False)}")
    print()

    # Phase 5 Results
    if result.get("quantum_state_created"):
        print("="*70)
        print("PHASE 5: Quantum-Inspired Optimization")
        print("="*70)
        metrics = result.get("quantum_metrics", {})
        print(f"Superposition Entropy: {metrics.get('entropy', 0):.4f}")
        print(f"State Purity: {metrics.get('purity', 0):.4f}")

        if result.get("quantum_optimized_tools"):
            print(f"Optimized Tools: {', '.join(result['quantum_optimized_tools'])}")

        if result.get("quantum_tunneling_solutions"):
            print(f"Tunneling Alternatives: {len(result['quantum_tunneling_solutions'])}")

        print(result.get("phase5_summary", ""))
    else:
        print("="*70)
        print("PHASE 5: Skipped (no tool execution or Phase 5 disabled)")
        print("="*70)

    print("\n" + "="*70)
    print("✓ Full Pipeline Execution Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
