#!/usr/bin/env python3
"""
Phase 7 Demo: Persistent Memory & Knowledge Integration

Demonstrates the complete 7-phase AGI framework with persistent memory,
historical knowledge retrieval, and continuous learning across sessions.
"""

from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager, ExecutionMemory


class FakeLLMPhase7:
    """Deterministic fake LLM for demo including Phase 7."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Phase 4a: Tool Selection
        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: math.add, text.uppercase
REASONING: Math for calculation, text for formatting
CONFIDENCE: 0.88"""

        # Phase 1: NLP
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: calculate sum and convert to uppercase
ENTITIES: numbers, calculation, text transformation
SUMMARY: Add two numbers and format the result"""

        # Phase 2: Knowledge
        if "synthesize" in prompt_lower or ("knowledge" in prompt_lower and "retrieve" in prompt_lower):
            return """KNOWLEDGE_POINTS: arithmetic operations and text transformations are common patterns
SYNTHESIS: Combining math with text is a valid pipeline
CONFIDENCE: 0.85"""

        # Phase 3a: Consciousness
        if "awareness" in prompt_lower or "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: numerical accuracy, text formatting consistency
METACOGNITION: Confident in both operations
CONFIDENCE: 0.78"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt_lower and ("causal" in prompt_lower or "analyze" in prompt_lower):
            return """REASONING_TYPE: multi-modal
CAUSAL: arithmetic produces results; text transforms content
LOGICAL: sequential execution is correct
PROBABILISTIC: high success probability
COMMON_SENSE: valid workflow
CONCLUSION: Approach is sound"""

        # Phase 3c: Creativity
        if "creative" in prompt_lower or "novelty" in prompt_lower:
            return """CREATIVE_IDEAS: pipeline math to text, chain transformations
ANALOGIES: like ETL data flow
CONCEPTUAL_BLEND: math + text = data pipeline
NOVELTY_SCORE: 72"""

        # Phase 4b: Parameter Binding
        if "parameter" in prompt_lower or "binding" in prompt_lower:
            return "a: 42\nb: 8"

        # Phase 4c: Tool Verification
        if "verif" in prompt_lower or "hallucination" in prompt_lower or "valid:" in prompt_lower:
            return """VALID: true
CONFIDENCE: 0.92
CONCERNS: none
REASONING: Results are correct"""

        # Phase 6: Learning
        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool selection strategy was effective
LESSON 2: Sequential math→text pattern works well
LESSON 3: Verification confirmed results
LESSON 4: High confidence indicates good reasoning
LESSON 5: Pipeline approach enables complex workflows"""

        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Leverage proven math→text pattern
SUGGESTION 2: Increase creativity phase exploration
SUGGESTION 3: Monitor execution times
SUGGESTION 4: Expand tool registry
SUGGESTION 5: Continue sequential execution"""

        # Phase 7: Memory synthesis
        if "similar" in prompt_lower and ("past" in prompt_lower or "execution" in prompt_lower):
            return """INSIGHT 1: Sequential math→text is a proven pattern
INSIGHT 2: Tool combinations work best in this order
INSIGHT 3: High verification confidence is important
INSIGHT 4: This approach scales well
CONFIDENCE: 0.92
RECOMMENDED_APPROACH: Use proven math→text pipeline for similar tasks"""

        return "RESULT: processed"


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_phase_header(phase: str, number: str):
    """Print phase header."""
    print(f"\n📊 Phase {number}: {phase}")
    print("-" * 70)


def main():
    """Run the complete Phase 1-7 integrated demo with persistent memory."""
    print_section("🚀 INTEGRATED AGI FRAMEWORK - FULL PHASE 1-7 PIPELINE DEMO")

    # Setup memory manager
    memory_manager = MemoryManager("demo_memory.json")
    print(f"💾 Using persistent memory (file: demo_memory.json)")
    print(f"   Current memory size: {memory_manager.get_memory_size()} executions")

    # Setup
    llm = FakeLLMPhase7()
    print("📡 Using FakeLLM (deterministic, reproducible)")

    registry = create_builtin_registry()
    safety_validator = SafetyValidator()
    print(f"📚 Loaded {len(registry.list_all())} built-in tools")

    coordinator = AgentCoordinator(
        llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=memory_manager,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        dry_run_mode=True,
    )
    print("🔧 AgentCoordinator initialized with Phase 1-7\n")

    # Input
    input_text = "Add 42 and 8, then convert the result to uppercase"
    print(f"🎯 Input: {input_text}\n")

    initial_state: FullAgentState = {
        "input_text": input_text,
    }

    print("⚙️  Processing through integrated Phase 1-7 pipeline...")
    print("-" * 70)

    # Execute full pipeline
    result = coordinator.invoke(initial_state)

    print("-" * 70)

    # Phase 1 Results
    print_phase_header("NLP Processing", "1")
    print(f"  Intent: {result.get('intent', 'N/A')}")
    print(f"  Entities: {', '.join(result.get('entities', []))}")

    # Phase 2 Results
    print_phase_header("Knowledge Retrieval", "2")
    knowledge = result.get('relevant_knowledge', 'N/A')
    print(f"  Knowledge: {knowledge[:70]}..." if len(str(knowledge)) > 70 else f"  Knowledge: {knowledge}")

    # Phase 3 Results
    print_phase_header("Consciousness & Reasoning", "3a-3c")
    print(f"  Attention: {', '.join(result.get('attention_focus', []))}")
    print(f"  Reasoning: {result.get('reasoning_type', 'N/A')}")
    print(f"  Creative Ideas: {len(result.get('creative_ideas', []))} ideas")

    # Phase 4 Results
    print_phase_header("Tool Selection & Execution", "4")
    print(f"  Selected: {', '.join(result.get('selected_tools', []))}")
    print(f"  Confidence: {result.get('tool_selection_confidence', 0):.2f}")

    if result.get("tool_execution_results"):
        print(f"  Executed: {len(result['tool_execution_results'])} tools")

    # Phase 5 Results
    if result.get("quantum_state_created"):
        print_phase_header("Quantum Optimization", "5")
        metrics = result.get("quantum_metrics", {})
        print(f"  Entropy: {metrics.get('entropy', 0):.4f}")
        print(f"  Purity: {metrics.get('purity', 0):.4f}")

    # Phase 6 Results
    print_phase_header("Learning & Feedback", "6")
    print(f"  Outcome: {result.get('execution_outcome', 'N/A').upper()}")
    print(f"  Confidence: {result.get('outcome_confidence', 0):.2f}")

    lessons = result.get("lessons_learned", [])
    if lessons:
        print(f"  📚 Lessons ({len(lessons)}):")
        for i, lesson in enumerate(lessons[:3], 1):
            print(f"     {i}. {lesson}")

    suggestions = result.get("improvement_suggestions", [])
    if suggestions:
        print(f"  💡 Suggestions ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"     {i}. {suggestion}")

    # Phase 7 Results - MAIN FOCUS
    print_phase_header("Persistent Memory & Knowledge", "7")

    print(f"  💾 Memory Status:")
    print(f"     Saved to persistent storage")
    print(f"     Total executions in memory: {result.get('memory_size', 0)}")
    print(f"     Similar past executions: {result.get('similar_past_executions', 0)}")

    if result.get("historical_lessons"):
        print(f"\n  📖 Historical Lessons:")
        for i, lesson in enumerate(result.get("historical_lessons", [])[:3], 1):
            print(f"     {i}. {lesson}")

    if result.get("historical_best_tools"):
        print(f"\n  🔧 Historical Best Tools:")
        for tool in result.get("historical_best_tools", []):
            print(f"     • {tool}")

    best_combos = result.get("best_tool_combinations", [])
    if best_combos:
        print(f"\n  🔗 Best Tool Combinations (Proven):")
        for i, combo in enumerate(best_combos[:3], 1):
            tools = " → ".join(combo.get("tools", []))
            success = combo.get("success_count", 0)
            print(f"     {i}. {tools} ({success} successes)")

    # Execution Statistics
    stats = result.get("execution_statistics", {})
    if stats.get("total_executions", 0) > 0:
        print(f"\n  📊 Execution Statistics:")
        print(f"     Total executions: {stats.get('total_executions', 0)}")
        print(f"     Success rate: {stats.get('success_rate', 0):.2%}")
        print(f"     Avg learning score: {stats.get('avg_learning_score', 0):.4f}")

    # Phase 7 Synthesis
    synthesis = result.get("phase7_synthesis", "")
    if synthesis:
        print(f"\n  🧠 Knowledge Synthesis:")
        lines = synthesis.split("\n")[:4]
        for line in lines:
            if line.strip():
                print(f"     {line}")

    insights = result.get("phase7_insights", [])
    if insights:
        print(f"\n  💡 Extracted Insights ({len(insights)}):")
        for i, insight in enumerate(insights[:3], 1):
            print(f"     {i}. {insight}")

    # Summary
    print_section("✅ PIPELINE COMPLETE - Full 7-Phase Execution with Persistent Memory")
    print(f"✓ LLM Calls: {llm.call_count}")
    print(f"✓ Phases 1-6: Analysis, reasoning, and learning")
    print(f"✓ Phase 7: Memory persistence and knowledge integration")
    print(f"✓ Total Memory Size: {result.get('memory_size', 0)} executions")

    print("\n🎯 AGI Framework Vision (7 Phases):")
    print("  • Phase 1: Understanding through NLP")
    print("  • Phase 2: Knowledge synthesis and retrieval")
    print("  • Phase 3: Consciousness, reasoning, and creativity")
    print("  • Phase 4: Strategic tool selection and execution")
    print("  • Phase 5: Quantum-inspired optimization")
    print("  • Phase 6: Learning and continuous improvement")
    print("  • Phase 7: Persistent memory and knowledge integration")

    print("\n💾 Persistent Memory Enabled:")
    print("  • Executions saved to disk for long-term learning")
    print("  • Similar past executions retrieved automatically")
    print("  • Lessons consolidated into knowledge base")
    print("  • Best tool combinations tracked and recommended")
    print("  • Execution statistics maintained across sessions")
    print("  • Historical patterns inform future decisions")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
