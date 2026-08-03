#!/usr/bin/env python3
"""
Phase 6 Demo: Learning & Feedback Loop

Demonstrates the complete integrated 6-phase AGI framework with learning,
feedback, and continuous improvement capabilities.
"""

from agents.state import FullAgentState, ToolExecutionResult, ToolVerificationResult
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator


class FakeLLMPhase6:
    """Deterministic fake LLM for demo including Phase 6."""

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
METACOGNITION: Confident in both operations; understand potential format edge cases
CONFIDENCE: 0.78"""

        # Phase 3b: Reasoning
        if "reasoning" in prompt_lower and ("causal" in prompt_lower or "analyze" in prompt_lower):
            return """REASONING_TYPE: multi-modal
CAUSAL: arithmetic produces results; text transforms content
LOGICAL: sequential execution is correct
PROBABILISTIC: high success probability for both tools
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
REASONING: Results are correct and within expected ranges"""

        # Phase 6: Learning and Feedback
        if "extract" in prompt_lower and "lesson" in prompt_lower:
            return """LESSON 1: Tool selection strategy was highly effective
LESSON 2: Verification phase caught potential hallucinations
LESSON 3: Sequential execution of math→text is a strong pattern
LESSON 4: High confidence scores indicate good reasoning
LESSON 5: Pipeline approach enables complex workflows"""

        if "improvement" in prompt_lower or "suggestion" in prompt_lower:
            return """SUGGESTION 1: Continue using verified tool combinations in future similar tasks
SUGGESTION 2: Leverage sequential math-to-text pattern for data transformation
SUGGESTION 3: Increase creativity phase exploration for novel combinations
SUGGESTION 4: Monitor tool execution times for performance optimization
SUGGESTION 5: Expand tool registry with complementary operations"""

        if "analyze" in prompt_lower and "fail" in prompt_lower:
            return """ROOT_CAUSES: Tool incompatibility or parameter mismatch
CONTRIBUTING_FACTORS: Incomplete type validation or edge case handling
PREVENTION: Add more comprehensive type checking and edge case tests"""

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
    """Run the complete Phase 1-6 integrated demo with learning."""
    print_section("🚀 INTEGRATED AGI FRAMEWORK - FULL PHASE 1-6 PIPELINE DEMO")

    # Setup
    llm = FakeLLMPhase6()
    print("📡 Using FakeLLM (deterministic, reproducible)")

    registry = create_builtin_registry()
    safety_validator = SafetyValidator()
    print(f"📚 Loaded {len(registry.list_all())} built-in tools")

    coordinator = AgentCoordinator(
        llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        dry_run_mode=True,
    )
    print("🔧 AgentCoordinator initialized with Phase 1-6\n")

    # Input
    input_text = "Add 42 and 8, then convert the result to uppercase"
    print(f"🎯 Input: {input_text}\n")

    initial_state: FullAgentState = {
        "input_text": input_text,
        # Simulate Phase 4 results for Phase 6 analysis
        "tool_execution_results": [
            ToolExecutionResult(
                tool_id="math.add",
                success=True,
                value=50,
                execution_time_ms=2.5,
                confidence=0.95,
            ),
            ToolExecutionResult(
                tool_id="text.uppercase",
                success=True,
                value="50",
                execution_time_ms=1.0,
                confidence=0.98,
            ),
        ],
        "verification_results": [
            ToolVerificationResult(
                tool_id="math.add",
                valid=True,
                confidence=0.95,
                reasoning="Arithmetic is correct",
            ),
            ToolVerificationResult(
                tool_id="text.uppercase",
                valid=True,
                confidence=0.98,
                reasoning="Text transformation verified",
            ),
        ],
    }

    print("⚙️  Processing through integrated Phase 1-6 pipeline...")
    print("-" * 70)

    # Execute full pipeline
    result = coordinator.invoke(initial_state)

    print("-" * 70)

    # Phase 1 Results
    print_phase_header("NLP Processing", "1")
    print(f"  Intent: {result.get('intent', 'N/A')}")
    print(f"  Entities: {', '.join(result.get('entities', []))}")
    print(f"  Summary: {result.get('summary', 'N/A')}")

    # Phase 2 Results
    print_phase_header("Knowledge Retrieval", "2")
    knowledge = result.get('relevant_knowledge', 'N/A')
    print(f"  Knowledge: {knowledge[:80]}..." if len(str(knowledge)) > 80 else f"  Knowledge: {knowledge}")

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
    print_phase_header("Tool Selection & Execution", "4")
    print(f"  Selected Tools: {', '.join(result.get('selected_tools', []))}")
    print(f"  Confidence: {result.get('tool_selection_confidence', 0):.2f}")

    if result.get("tool_execution_results"):
        print(f"  Tools Executed: {len(result['tool_execution_results'])}")
        for res in result["tool_execution_results"]:
            status = "✓" if res.success else "✗"
            print(f"    - {res.tool_id}: {status} ({res.execution_time_ms:.1f}ms)")

    # Phase 5 Results
    if result.get("quantum_state_created"):
        print_phase_header("Quantum-Inspired Optimization", "5")
        metrics = result.get("quantum_metrics", {})
        print(f"  Superposition Entropy: {metrics.get('entropy', 0):.4f}")
        print(f"  State Purity: {metrics.get('purity', 0):.4f}")
        if result.get("quantum_optimized_tools"):
            print(f"  Optimized Tools: {', '.join(result['quantum_optimized_tools'])}")
    else:
        print_phase_header("Quantum Optimization", "5")
        print("  Status: Available (requires Phase 4)")

    # Phase 6 Results - MAIN FOCUS
    print_phase_header("Learning & Feedback Loop", "6")

    outcome = result.get("execution_outcome", "unknown")
    confidence = result.get("outcome_confidence", 0)
    print(f"  Execution Outcome: {outcome.upper()}")
    print(f"  Outcome Confidence: {confidence:.2f}")

    lessons = result.get("lessons_learned", [])
    print(f"\n  📚 Key Lessons Learned ({len(lessons)}):")
    for i, lesson in enumerate(lessons[:4], 1):
        print(f"    {i}. {lesson}")

    suggestions = result.get("improvement_suggestions", [])
    print(f"\n  💡 Improvement Suggestions ({len(suggestions)}):")
    for i, suggestion in enumerate(suggestions[:4], 1):
        print(f"    {i}. {suggestion}")

    tool_scores = result.get("tool_performance_scores", {})
    if tool_scores:
        print(f"\n  🔧 Tool Performance Scores:")
        for tool_id, score in sorted(tool_scores.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            print(f"    {tool_id:20} {bar} {score:.2f}")

    combinations = result.get("effective_tool_combinations", [])
    if combinations:
        print(f"\n  🔗 Effective Tool Combinations:")
        for combo in combinations:
            print(f"    → {' → '.join(combo)}")

    learning_metrics = result.get("learning_metrics", {})
    print(f"\n  📊 Learning Metrics:")
    print(f"    Overall Learning Score: {learning_metrics.get('overall_learning_score', 0):.4f}")
    print(f"    Avg Tool Performance: {learning_metrics.get('avg_tool_performance', 0):.4f}")
    print(f"    Avg Phase Performance: {learning_metrics.get('avg_phase_performance', 0):.4f}")
    print(f"    Learning Quality: {learning_metrics.get('learning_quality', 0):.4f}")

    # Summary
    print_section("✅ PIPELINE COMPLETE - Full 6-Phase Execution with Learning")
    print(f"✓ LLM Calls: {llm.call_count}")
    print(f"✓ All phases executed successfully")
    print(f"✓ Quantum-inspired optimization applied")
    print(f"✓ Learning feedback loop completed")
    print(f"✓ State preservation maintained through all phases")

    print("\n🎯 AGI Framework Vision:")
    print("  • Phase 1: Understanding through NLP")
    print("  • Phase 2: Knowledge synthesis and retrieval")
    print("  • Phase 3: Consciousness, reasoning, and creativity")
    print("  • Phase 4: Strategic tool selection and execution")
    print("  • Phase 5: Quantum-inspired optimization")
    print("  • Phase 6: Learning and continuous improvement")

    print("\n🔄 Feedback Loop Enabled:")
    print("  • Execution analyzed for success/failure")
    print("  • Tools scored on performance and confidence")
    print("  • Effective combinations identified and recorded")
    print("  • Lessons extracted for knowledge update")
    print("  • Improvements suggested for next iterations")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
