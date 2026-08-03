"""Phase 7: Persistent Memory & Knowledge Integration."""

from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState
from learning.memory_manager import MemoryManager, ExecutionMemory

LLMFn = Callable[[str], str]


def make_memory_persistence_node(llm: LLMFn, memory_manager: MemoryManager):
    """
    Create Phase 7a memory persistence node.

    Saves current execution to persistent memory and retrieves relevant
    historical knowledge to inform future decisions.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 7a: Memory Persistence.

        Saves current execution learnings and retrieves historical insights.
        """
        # Extract Phase 6 learning results
        execution_outcome = state.get("execution_outcome", "unknown")
        lessons_learned = state.get("lessons_learned", [])
        tool_scores = state.get("tool_performance_scores", {})
        effective_tools = state.get("selected_tools", [])
        suggestions = state.get("improvement_suggestions", [])
        learning_metrics = state.get("learning_metrics", {})
        input_text = state.get("input_text", "")

        # Save current execution to memory
        memory = ExecutionMemory(
            input_text=input_text,
            execution_outcome=execution_outcome,
            lessons_learned=lessons_learned,
            tool_performance_scores=tool_scores,
            effective_tools=effective_tools,
            improvement_suggestions=suggestions,
            learning_metrics=learning_metrics,
        )
        memory_manager.add_memory(memory)

        # Retrieve similar past executions
        similar_executions = memory_manager.find_similar_executions(
            input_text, similarity_threshold=0.4
        )

        # Extract insights from similar executions
        historical_lessons = _extract_historical_lessons(similar_executions)
        historical_tools = _extract_historical_tools(similar_executions)
        historical_suggestions = _extract_historical_suggestions(
            similar_executions
        )

        # Get best tool combinations overall
        best_combinations = memory_manager.get_best_tool_combinations(limit=5)

        # Get statistics
        execution_stats = memory_manager.get_execution_statistics()
        tool_stats = memory_manager.get_tool_statistics()

        # Get common lessons and suggestions
        common_lessons = memory_manager.get_common_lessons(limit=5)
        high_confidence_suggestions = (
            memory_manager.get_high_confidence_suggestions(limit=5)
        )

        # Update state with Phase 7 results
        state.update({
            "memory_persisted": True,
            "memory_size": memory_manager.get_memory_size(),
            "similar_past_executions": len(similar_executions),
            "historical_lessons": historical_lessons,
            "historical_best_tools": historical_tools,
            "historical_suggestions": historical_suggestions,
            "best_tool_combinations": best_combinations,
            "execution_statistics": execution_stats,
            "tool_statistics": tool_stats,
            "common_lessons": common_lessons,
            "high_confidence_suggestions": high_confidence_suggestions,
        })

        return state

    return process


def make_memory_retrieval_node(llm: LLMFn, memory_manager: MemoryManager):
    """
    Create Phase 7b memory retrieval node.

    Retrieves and synthesizes relevant historical knowledge for
    current task using LLM analysis.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """
        Execute Phase 7b: Memory Retrieval & Synthesis.

        Analyzes past experiences and generates contextualized advice.
        """
        input_text = state.get("input_text", "")
        similar_executions = memory_manager.find_similar_executions(
            input_text, similarity_threshold=0.3
        )

        if not similar_executions:
            state.update({
                "phase7_synthesis": "No similar past executions found. Starting fresh.",
                "phase7_insights": [],
                "phase7_confidence": 0.0,
            })
            return state

        # Build context from similar executions
        context = _build_similarity_context(similar_executions)

        # Use LLM to synthesize insights
        prompt = f"""Based on these similar past executions, provide insights for this task:

Current Task: {input_text}

Similar Past Executions:
{context}

Provide insights in this format:
INSIGHT 1: [key insight]
INSIGHT 2: [key insight]
INSIGHT 3: [key insight]
CONFIDENCE: [0.0-1.0]
RECOMMENDED_APPROACH: [recommended strategy]"""

        response = llm(prompt)
        insights = _parse_synthesis_response(response)

        phase7_summary = _generate_phase7_summary(
            similar_executions, insights
        )

        state.update({
            "phase7_synthesis": phase7_summary,
            "phase7_insights": insights.get("insights", []),
            "phase7_confidence": insights.get("confidence", 0.5),
            "phase7_recommended_approach": insights.get(
                "recommended_approach", ""
            ),
        })

        return state

    return process


def _extract_historical_lessons(
    similar_executions: list[tuple]
) -> list[str]:
    """Extract unique lessons from similar past executions."""
    all_lessons = set()

    for memory, _ in similar_executions[:5]:  # Top 5 similar
        all_lessons.update(memory.lessons_learned)

    return list(all_lessons)[:5]


def _extract_historical_tools(
    similar_executions: list[tuple]
) -> list[str]:
    """Extract effective tools from similar past executions."""
    tool_frequencies = {}

    for memory, _ in similar_executions[:5]:
        for tool in memory.effective_tools:
            tool_frequencies[tool] = tool_frequencies.get(tool, 0) + 1

    # Sort by frequency
    sorted_tools = sorted(
        tool_frequencies.items(), key=lambda x: x[1], reverse=True
    )

    return [tool for tool, _ in sorted_tools[:3]]


def _extract_historical_suggestions(
    similar_executions: list[tuple]
) -> list[str]:
    """Extract improvement suggestions from similar past executions."""
    all_suggestions = []

    for memory, _ in similar_executions[:5]:
        all_suggestions.extend(memory.improvement_suggestions)

    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for sugg in all_suggestions:
        if sugg not in seen:
            seen.add(sugg)
            unique_suggestions.append(sugg)

    return unique_suggestions[:3]


def _build_similarity_context(
    similar_executions: list[tuple],
) -> str:
    """Build context string from similar executions."""
    lines = []

    for i, (memory, similarity) in enumerate(similar_executions[:3], 1):
        lines.append(f"\nExecution {i} (Similarity: {similarity:.2%}):")
        lines.append(f"  Input: {memory.input_text[:60]}...")
        lines.append(f"  Outcome: {memory.execution_outcome}")
        lines.append(f"  Lessons: {'; '.join(memory.lessons_learned[:2])}")
        lines.append(
            f"  Effective Tools: {', '.join(memory.effective_tools)}"
        )

    return "\n".join(lines)


def _parse_synthesis_response(response: str) -> dict:
    """Parse LLM synthesis response."""
    insights = []
    confidence = 0.5
    recommended_approach = ""

    lines = response.split("\n")
    for line in lines:
        if line.startswith("INSIGHT"):
            insight = line.split(":", 1)[-1].strip()
            if insight:
                insights.append(insight)
        elif line.startswith("CONFIDENCE"):
            try:
                confidence = float(line.split(":", 1)[-1].strip())
            except (ValueError, IndexError):
                confidence = 0.5
        elif line.startswith("RECOMMENDED_APPROACH"):
            recommended_approach = line.split(":", 1)[-1].strip()

    return {
        "insights": insights,
        "confidence": confidence,
        "recommended_approach": recommended_approach,
    }


def _generate_phase7_summary(
    similar_executions: list[tuple],
    insights: dict,
) -> str:
    """Generate human-readable Phase 7 summary."""
    summary_lines = [
        "=== Phase 7: Persistent Memory & Knowledge Integration ===",
        f"Similar Past Executions Found: {len(similar_executions)}",
    ]

    if similar_executions:
        summary_lines.append(f"Best Match Similarity: {similar_executions[0][1]:.2%}")
        summary_lines.append(f"Top Match Outcome: {similar_executions[0][0].execution_outcome.upper()}")

    if insights.get("insights"):
        summary_lines.append(f"\nExtracted Insights ({len(insights['insights'])}):")
        for i, insight in enumerate(insights["insights"][:3], 1):
            summary_lines.append(f"  {i}. {insight}")

    summary_lines.append(
        f"\nKnowledge Integration Confidence: {insights.get('confidence', 0):.2f}"
    )

    if insights.get("recommended_approach"):
        summary_lines.append(
            f"Recommended Approach: {insights['recommended_approach']}"
        )

    return "\n".join(summary_lines)


def make_phase7_summary_node(llm: LLMFn):
    """
    Create Phase 7 summary node.

    Generates comprehensive summary of memory operations and knowledge synthesis.
    """

    def process(state: FullAgentState) -> FullAgentState:
        """Generate summary of Phase 7 results."""
        summary_lines = [
            "=== Phase 7: Persistent Memory & Knowledge Integration ===",
            f"Execution saved to memory (Total: {state.get('memory_size', 0)})",
            f"Similar past executions found: {state.get('similar_past_executions', 0)}",
        ]

        # Historical context
        lessons = state.get("historical_lessons", [])
        if lessons:
            summary_lines.append(f"\nHistorical Lessons Extracted ({len(lessons)}):")
            for i, lesson in enumerate(lessons[:3], 1):
                summary_lines.append(f"  {i}. {lesson}")

        # Tool recommendations from history
        tools = state.get("historical_best_tools", [])
        if tools:
            summary_lines.append(f"\nHistorically Effective Tools:")
            for tool in tools[:3]:
                summary_lines.append(f"  • {tool}")

        # Statistics
        stats = state.get("execution_statistics", {})
        if stats:
            summary_lines.extend([
                f"\nExecution History Statistics:",
                f"  Total Executions: {stats.get('total_executions', 0)}",
                f"  Success Rate: {stats.get('success_rate', 0):.2%}",
                f"  Avg Learning Score: {stats.get('avg_learning_score', 0):.4f}",
            ])

        # Best combinations
        combos = state.get("best_tool_combinations", [])
        if combos:
            summary_lines.append(f"\nBest Tool Combinations from History:")
            for i, combo in enumerate(combos[:3], 1):
                tools_str = " → ".join(combo.get("tools", []))
                success = combo.get("success_count", 0)
                summary_lines.append(
                    f"  {i}. {tools_str} (Success: {success}x)"
                )

        # Phase 7 synthesis
        synthesis = state.get("phase7_synthesis", "")
        if synthesis:
            summary_lines.append(f"\nMemory Synthesis:")
            for line in synthesis.split("\n")[:5]:
                summary_lines.append(f"  {line}")

        phase7_summary = "\n".join(summary_lines)

        state.update({
            "phase7_summary": phase7_summary,
        })

        return state

    return process
