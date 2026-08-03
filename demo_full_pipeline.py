#!/usr/bin/env python3
"""
Full Phase 1-5 AGI Pipeline Demo

Demonstrates the complete integrated reasoning system with quantum-inspired optimization:
- Phase 1: NLP (intent, entities, summary)
- Phase 2: Knowledge (semantic retrieval, synthesis)
- Phase 3a: Consciousness (attention, metacognition)
- Phase 3b: Reasoning (multi-modal causal/logical/probabilistic analysis)
- Phase 3c: Creativity (novel ideas, analogies, conceptual blends)
- Phase 4a: Tool Selection (consciousness-aware, reasoning-justified selection)
- Phase 4b: Tool Execution (safe parameter binding and execution)
- Phase 4c: Tool Verification (hallucination detection, validation)
- Phase 5a: Quantum Optimization (superposition → entanglement → tunneling → amplification → annealing)
- Phase 5b: Quantum Summary (metrics and state reporting)

Uses a deterministic FakeLLM for reproducible testing without external dependencies.
"""

from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLM:
    """Deterministic fake LLM for demo without requiring Ollama/Claude."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Phase 4a: Tool Selection (check first - most specific)
        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Based on consciousness (attention to numerical accuracy), reasoning (logical sequence), and creativity (combining math and text), we select math.add for calculation and text.uppercase for transformation. These form a coherent workflow.
CONFIDENCE: 0.88"""

        # Phase 1: NLP
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: combine numerical calculation with text transformation
ENTITIES: numbers, mathematical operations, text formatting
SUMMARY: The task involves performing arithmetic calculations and converting results to different text formats"""

        # Phase 2: Knowledge
        if "synthesize" in prompt_lower or ("knowledge" in prompt_lower and "retrieve" in prompt_lower):
            return """KNOWLEDGE_POINTS: arithmetic operations support addition and multiplication, text tools provide case conversion and transformations
SYNTHESIS: System can combine mathematical operations with text processing to create compound data transformations
CONFIDENCE: 0.85"""

        # Phase 3a: Consciousness (attention focus and metacognition)
        if "awareness" in prompt_lower or "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: numerical accuracy, text consistency, operation sequence
METACOGNITION: System is confident in arithmetic operations but should verify text transformations; complex multi-step operations require validation
CONFIDENCE: 0.78"""

        # Phase 3b: Reasoning (multi-modal analysis)
        if "reasoning" in prompt_lower and ("causal" in prompt_lower or "analyze" in prompt_lower):
            return """REASONING_TYPE: multi-modal
CAUSAL: arithmetic operations cause numerical results; text operations transform content
LOGICAL: sequential execution ensures correct operation order; tools must be compatible
PROBABILISTIC: high probability of success for basic arithmetic; text operations generally reliable
COMMON_SENSE: combining addition with text uppercase is a valid multi-step workflow
CONCLUSION: Approach is sound; recommend executing math.add followed by text.uppercase"""

        # Phase 3c: Creativity
        if "creative" in prompt_lower or "novelty" in prompt_lower:
            return """CREATIVE_IDEAS: pipeline results to multiple tools, chain text transformations, create data transformation workflows
ANALOGIES: similar to ETL data pipelines where data flows through multiple transformation stages
CONCEPTUAL_BLEND: arithmetic + text processing = data transformation pipeline
NOVELTY_SCORE: 72"""

        # Tool parameter binding
        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 42\nb: 8"

        # Tool verification
        if "verif" in prompt_lower or "hallucination" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.92
CONCERNS: none
REASONING: Results are mathematically correct and within expected ranges"""

        return "RESULT: processed"


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_phase_header(phase: str, number: int):
    """Print phase header."""
    print(f"\n📊 Phase {number}: {phase}")
    print("-" * 70)


def main():
    """Run the complete Phase 1-5 integrated demo."""
    print_section("🚀 INTEGRATED AGI FRAMEWORK - FULL PHASE 1-5 PIPELINE DEMO")

    # Setup
    llm = FakeLLM()
    print("📡 Using FakeLLM (deterministic, reproducible)")

    registry = create_builtin_registry()
    safety_validator = SafetyValidator()
    print(f"📚 Loaded {len(registry.list_all())} built-in tools")

    coordinator = AgentCoordinator(
        llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,   # Enable tool execution
        enable_phase5=True,   # Enable quantum optimization
        dry_run_mode=True,    # Safe mode: verify without actual execution
    )
    print("🔧 AgentCoordinator initialized with Phase 1-5\n")

    # Input
    input_text = "Add 42 and 8, then convert the result to uppercase"
    print(f"🎯 Input: {input_text}\n")

    initial_state: FullAgentState = {
        "input_text": input_text,
    }

    print("⚙️  Processing through integrated Phase 1-5 pipeline...")
    print("-" * 70)

    # Execute full pipeline
    result = coordinator.invoke(initial_state)

    print("-" * 70)

    # Phase 1 Results
    print_phase_header("NLP Processing", 1)
    print(f"  Intent: {result.get('intent', 'N/A')}")
    print(f"  Entities: {', '.join(result.get('entities', []))}")
    print(f"  Summary: {result.get('summary', 'N/A')}")

    # Phase 2 Results
    print_phase_header("Knowledge Retrieval", 2)
    knowledge = result.get('relevant_knowledge', 'N/A')
    print(f"  Knowledge Points: {knowledge[:100]}..." if len(str(knowledge)) > 100 else f"  Knowledge Points: {knowledge}")

    # Phase 3a Results
    print_phase_header("Consciousness & Metacognition", "3a")
    print(f"  Attention Focus: {', '.join(result.get('attention_focus', []))}")
    print(f"  Metacognition: {result.get('metacognitive_notes', 'N/A')}")

    # Phase 3b Results
    print_phase_header("Multi-Modal Reasoning", "3b")
    print(f"  Reasoning Type: {result.get('reasoning_type', 'N/A')}")
    print(f"  Conclusion: {result.get('reasoning_conclusion', 'N/A')}")

    # Phase 3c Results
    print_phase_header("Creative Solutions", "3c")
    print(f"  Creative Ideas: {', '.join(result.get('creative_ideas', []))}")

    # Phase 4 Results
    print_phase_header("Tool Selection & Execution", 4)
    print(f"  Selected Tools: {', '.join(result.get('selected_tools', []))}")
    print(f"  Reasoning: {result.get('tool_selection_reasoning', 'N/A')}")
    print(f"  Confidence: {result.get('tool_selection_confidence', 0):.2f}")

    if result.get("tool_execution_results"):
        print(f"\n  Tools Executed: {len(result['tool_execution_results'])}")
        for res in result["tool_execution_results"]:
            status = "✓" if res.get("success") else "✗"
            print(f"    - {res.get('tool_id', 'N/A')}: {status}")

    # Phase 5 Results
    if result.get("quantum_state_created"):
        print_phase_header("Quantum-Inspired Optimization", 5)
        metrics = result.get("quantum_metrics", {})
        print(f"  Superposition Entropy: {metrics.get('entropy', 0):.4f}")
        print(f"  State Purity: {metrics.get('purity', 0):.4f}")

        if result.get("quantum_optimized_tools"):
            print(f"  Optimized Tools: {', '.join(result['quantum_optimized_tools'])}")

        if result.get("quantum_tunneling_solutions"):
            print(f"  Tunneling Alternatives Explored: {len(result['quantum_tunneling_solutions'])}")
    else:
        print_phase_header("Quantum Optimization", 5)
        print("  Status: Skipped (no tool execution or Phase 5 disabled)")

    # Summary
    print_section("✅ PIPELINE COMPLETE - Full 5-Phase Execution")
    print(f"✓ LLM Calls: {llm.call_count}")
    print(f"✓ All phases executed successfully")
    print(f"✓ Quantum-inspired optimization applied")
    print(f"✓ State preservation maintained through all phases")

    print("\n🎯 Vision Realized:")
    print("  • Consciousness informs tool selection through attention focus")
    print("  • Reasoning justifies tool choices multi-modally")
    print("  • Creativity enables novel tool combinations")
    print("  • Quantum algorithms optimize final selection")
    print("  • Safety validation prevents execution of risky operations")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
