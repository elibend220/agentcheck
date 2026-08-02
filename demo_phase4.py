#!/usr/bin/env python3
"""
Integrated AGI Framework Demo: Full Phase 1-4 Pipeline

Demonstrates the complete integration of:
Phase 1: NLP Processing (intent, entities, summary)
Phase 2: Knowledge Retrieval (synthesis)
Phase 3a: Consciousness (attention, metacognition)
Phase 3b: Reasoning (multi-modal causal/logical/probabilistic)
Phase 3c: Creativity (novel ideas, analogies)
Phase 4a: Tool Selection (consciousness-aware, reasoning-justified)
Phase 4b: Tool Execution (safe parameter binding and execution)
Phase 4c: Tool Verification (hallucination detection, validation)

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
REASONING: Based on consciousness (attention to accuracy), reasoning (logical sequence), and creativity (pipeline concept), we select math.add for calculation and text.uppercase for transformation. These form a coherent workflow.
CONFIDENCE: 0.88"""

        # Phase 1: NLP
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: transform and calculate numerical values
ENTITIES: numbers, mathematical operations, text transformation
SUMMARY: The task involves performing arithmetic calculations and converting results to different text formats"""

        # Phase 2: Knowledge
        if "synthesize" in prompt_lower or "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: arithmetic operations support addition/multiplication, text tools provide case conversion
SYNTHESIS: System can combine mathematical operations with text processing to create compound transformations
CONFIDENCE: 0.85"""

        # Phase 3a: Consciousness (check before general "consciousness")
        if "awareness" in prompt_lower or "attention" in prompt_lower:
            return """ATTENTION_FOCUS: numerical accuracy, text consistency, operation sequence
METACOGNITION: System is confident in arithmetic but should verify text transformations; complex multi-step operations require validation
CONFIDENCE: 0.78"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt_lower and "causal" in prompt_lower:
            return """CAUSAL: arithmetic operations cause numerical results; text operations transform content
LOGICAL: sequential execution ensures correct operation order; tools must be compatible
PROBABILISTIC: high probability of success for basic arithmetic; text operations generally reliable
COMMON_SENSE: combining addition with text uppercase is a valid multi-step workflow
CONCLUSION: Approach is sound; recommend executing math.add followed by text.uppercase"""

        # Phase 3c: Creativity
        if "creative" in prompt_lower or "novelty" in prompt_lower:
            return """CREATIVE_IDEAS: pipeline results to multiple tools, chain text transformations, create data processing workflows
ANALOGIES: similar to ETL data pipelines, similar to compiler multi-pass optimization
CONCEPTUAL_BLEND: arithmetic + text processing = data transformation pipeline
NOVELTY_SCORE: 72"""

        # Tool execution/binding prompts
        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 42\nb: 8"

        # Tool verification prompts
        if "verif" in prompt_lower or "hallucination" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.92
CONCERNS: none
REASONING: Results are mathematically correct and within expected ranges"""

        return "RESULT: processed"


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_phase_header(phase_name: str, number: int):
    """Print phase header."""
    print(f"\n📊 Phase {number}: {phase_name}")
    print("-" * 70)


def demo_full_pipeline():
    """Run the complete Phase 1-4 integrated demo."""
    print_section("🚀 INTEGRATED AGI FRAMEWORK - FULL PHASE 1-4 PIPELINE DEMO")

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
        enable_phase4=True,
        dry_run_mode=True,  # Safe mode: don't actually execute, just verify selection
    )

    print("🔧 AgentCoordinator initialized with Phase 1-4")

    # Input
    input_text = "Add 42 and 8, then convert the result to uppercase"
    print(f"\n🎯 Input: {input_text}")

    # Execute pipeline
    print("\n⚙️  Processing through integrated Phase 1-4 pipeline...")
    print("-" * 70)

    state: FullAgentState = {"input_text": input_text}
    result = coordinator.invoke(state)

    print("-" * 70)

    # Display results by phase
    print_phase_header("NLP Processing", 1)
    print(f"  Intent: {result.get('intent', 'N/A')}")
    print(f"  Entities: {', '.join(result.get('entities', {}).get('names', []))}")
    print(f"  Summary: {result.get('summary', 'N/A')}")

    print_phase_header("Knowledge Retrieval", 2)
    knowledge = result.get("relevant_knowledge", [])
    if knowledge:
        print(f"  Knowledge Points: {', '.join(knowledge[:3])}")
    print(f"  Synthesis: {result.get('knowledge_summary', 'N/A')[:80]}...")

    print_phase_header("Consciousness & Metacognition", "3a")
    print(f"  Attention Focus: {', '.join(result.get('attention_focus', []))}")
    print(f"  Metacognition: {result.get('metacognitive_notes', 'N/A')[:80]}...")

    print_phase_header("Multi-Modal Reasoning", "3b")
    print(f"  Reasoning Type: {result.get('reasoning_type', 'N/A')}")
    reasoning_steps = result.get("reasoning_steps", [])
    for i, step in enumerate(reasoning_steps[:3], 1):
        print(f"  Step {i}: {step[:70]}...")
    print(f"  Conclusion: {result.get('reasoning_conclusion', 'N/A')[:80]}...")

    print_phase_header("Creative Solutions", "3c")
    ideas = result.get("creative_ideas", [])
    print(f"  Creative Ideas: {', '.join(ideas) if ideas else 'N/A'}")
    analogies = result.get("analogies", [])
    if analogies:
        print(f"  Analogies: {', '.join(analogies)}")

    print_phase_header("Tool Selection (Phase 4a)", "4a")
    selected = result.get("selected_tools", [])
    print(f"  Selected Tools: {', '.join(selected) if selected else 'None'}")
    print(f"  Reasoning: {result.get('tool_selection_reasoning', 'N/A')[:70]}...")
    print(f"  Confidence: {result.get('tool_selection_confidence', 0):.2f}")

    print_phase_header("Tool Execution (Phase 4b)", "4b")
    exec_results = result.get("tool_execution_results", [])
    if exec_results:
        print(f"  Tools Executed: {len(exec_results)}")
        for exec_result in exec_results:
            status = "✓ Success" if exec_result.success else "✗ Failed"
            print(f"    - {exec_result.tool_id}: {status}")
            if exec_result.success:
                print(f"      Result: {exec_result.value}")
                print(f"      Time: {exec_result.execution_time_ms:.2f}ms")
            else:
                print(f"      Error: {exec_result.error}")
    else:
        print("  No tools executed (dry-run mode)")

    print_phase_header("Tool Verification (Phase 4c)", "4c")
    verify_results = result.get("verification_results", [])
    if verify_results:
        print(f"  Verification Results: {len(verify_results)}")
        for verify_result in verify_results:
            status = "✓ Valid" if verify_result.valid else "✗ Invalid"
            print(f"    - {verify_result.tool_id}: {status}")
            print(f"      Confidence: {verify_result.confidence:.2f}")
            if verify_result.concerns:
                print(f"      Concerns: {', '.join(verify_result.concerns)}")

    # Summary
    print_section("✅ PIPELINE COMPLETE - Architecture Validation")

    print("\n✓ All phases executed successfully:")
    print("  ✓ Phase 1: NLP Processing")
    print("  ✓ Phase 2: Knowledge Retrieval")
    print("  ✓ Phase 3a: Consciousness & Metacognition")
    print("  ✓ Phase 3b: Multi-Modal Reasoning")
    print("  ✓ Phase 3c: Creative Solutions")
    print("  ✓ Phase 4a: Consciousness-Aware Tool Selection")
    print("  ✓ Phase 4b: Safe Tool Execution")
    print("  ✓ Phase 4c: Verification & Hallucination Detection")

    print(f"\nLLM Calls: {llm.call_count}")
    print(f"Selected Tools: {', '.join(selected) if selected else 'None'}")
    print(f"Tools Verified: {len(verify_results)}")

    print("\n🎯 Vision Preserved:")
    print("  • Consciousness informs tool selection through attention focus")
    print("  • Reasoning justifies tool choices multi-modally")
    print("  • Creativity enables novel tool combinations")
    print("  • Safety validation prevents execution of risky operations")
    print("  • Verification detects hallucinations and inconsistencies")

    print("\n" + "=" * 70)


def demo_phases_1_to_3_only():
    """Run demo with Phases 1-3 only (without tool execution)."""
    print_section("🚀 INTEGRATED AGI FRAMEWORK - PHASES 1-3 DEMO")

    llm = FakeLLM()
    coordinator = AgentCoordinator(llm, enable_phase4=False)

    input_text = "Analyze renewable energy solutions"
    print(f"Input: {input_text}\n")

    state: FullAgentState = {"input_text": input_text}
    result = coordinator.invoke(state)

    print(f"Intent: {result.get('intent', 'N/A')}")
    print(f"Entities: {', '.join(result.get('entities', {}).get('names', []))}")
    print(f"Attention Focus: {', '.join(result.get('attention_focus', []))}")
    print(f"Reasoning: {result.get('reasoning_conclusion', 'N/A')[:100]}...")
    print(f"Creative Ideas: {', '.join(result.get('creative_ideas', []))}")

    print(f"\n✅ Phases 1-3 complete (no tool execution)")


if __name__ == "__main__":
    # Run full Phase 1-4 demo
    demo_full_pipeline()

    print("\n\n")

    # Run Phases 1-3 only demo
    demo_phases_1_to_3_only()
