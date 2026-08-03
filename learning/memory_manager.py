"""Persistent memory manager for AGI framework."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class ExecutionMemory:
    """Record of a single execution with learnings."""

    def __init__(
        self,
        input_text: str,
        execution_outcome: str,
        lessons_learned: list[str],
        tool_performance_scores: dict[str, float],
        effective_tools: list[str],
        improvement_suggestions: list[str],
        learning_metrics: dict[str, float],
        timestamp: Optional[str] = None,
    ):
        self.input_text = input_text
        self.execution_outcome = execution_outcome
        self.lessons_learned = lessons_learned
        self.tool_performance_scores = tool_performance_scores
        self.effective_tools = effective_tools
        self.improvement_suggestions = improvement_suggestions
        self.learning_metrics = learning_metrics
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "input_text": self.input_text,
            "execution_outcome": self.execution_outcome,
            "lessons_learned": self.lessons_learned,
            "tool_performance_scores": self.tool_performance_scores,
            "effective_tools": self.effective_tools,
            "improvement_suggestions": self.improvement_suggestions,
            "learning_metrics": self.learning_metrics,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ExecutionMemory:
        """Create from dictionary."""
        return cls(**data)


class MemoryManager:
    """Manages persistent memory of past executions."""

    def __init__(self, memory_file: str = "execution_memory.json"):
        self.memory_file = Path(memory_file)
        self.memories: list[ExecutionMemory] = []
        self.load()

    def load(self):
        """Load memories from disk."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    self.memories = [ExecutionMemory.from_dict(m) for m in data]
            except (json.JSONDecodeError, KeyError):
                self.memories = []
        else:
            self.memories = []

    def save(self):
        """Save memories to disk."""
        with open(self.memory_file, "w") as f:
            json.dump([m.to_dict() for m in self.memories], f, indent=2)

    def add_memory(self, memory: ExecutionMemory):
        """Add a new execution memory."""
        self.memories.append(memory)
        self.save()

    def get_all_memories(self) -> list[ExecutionMemory]:
        """Get all stored memories."""
        return self.memories

    def find_similar_executions(
        self,
        input_text: str,
        similarity_threshold: float = 0.5,
    ) -> list[tuple[ExecutionMemory, float]]:
        """
        Find similar past executions using simple string similarity.

        Returns list of (memory, similarity_score) tuples, sorted by similarity.
        """
        from difflib import SequenceMatcher

        similarities = []
        input_lower = input_text.lower()

        for memory in self.memories:
            memory_lower = memory.input_text.lower()
            ratio = SequenceMatcher(None, input_lower, memory_lower).ratio()

            if ratio >= similarity_threshold:
                similarities.append((memory, ratio))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def get_best_tool_combinations(self, limit: int = 5) -> list[dict[str, Any]]:
        """Get the most successful tool combinations."""
        combination_stats = {}

        for memory in self.memories:
            if memory.execution_outcome == "success":
                key = tuple(sorted(memory.effective_tools))
                if key not in combination_stats:
                    combination_stats[key] = {
                        "tools": list(key),
                        "success_count": 0,
                        "avg_performance": 0.0,
                        "lessons": [],
                    }

                combination_stats[key]["success_count"] += 1
                scores = [
                    memory.tool_performance_scores.get(t, 0) for t in key
                ]
                if scores:
                    combination_stats[key]["avg_performance"] = sum(scores) / len(
                        scores
                    )
                combination_stats[key]["lessons"].extend(memory.lessons_learned)

        # Sort by success count and average performance
        sorted_combos = sorted(
            combination_stats.values(),
            key=lambda x: (x["success_count"], x["avg_performance"]),
            reverse=True,
        )

        return sorted_combos[:limit]

    def get_common_lessons(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get most frequently learned lessons."""
        lesson_counts = {}

        for memory in self.memories:
            for lesson in memory.lessons_learned:
                lesson_counts[lesson] = lesson_counts.get(lesson, 0) + 1

        # Sort by frequency
        sorted_lessons = sorted(
            lesson_counts.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_lessons[:limit]

    def get_high_confidence_suggestions(self, limit: int = 10) -> list[str]:
        """Get improvement suggestions that appear frequently."""
        suggestion_counts = {}

        for memory in self.memories:
            for suggestion in memory.improvement_suggestions:
                suggestion_counts[suggestion] = (
                    suggestion_counts.get(suggestion, 0) + 1
                )

        # Filter suggestions that appear multiple times (high confidence)
        frequent_suggestions = [
            (sugg, count)
            for sugg, count in suggestion_counts.items()
            if count >= 2
        ]

        # Sort by frequency
        frequent_suggestions.sort(key=lambda x: x[1], reverse=True)

        return [sugg for sugg, _ in frequent_suggestions[:limit]]

    def get_tool_win_rate(self, tool_id: str) -> float:
        """Calculate win rate for a specific tool across all memories."""
        if not self.memories:
            return 0.0

        success_count = 0
        total_uses = 0

        for memory in self.memories:
            if tool_id in memory.effective_tools:
                total_uses += 1
                if memory.execution_outcome == "success":
                    success_count += 1

        if total_uses == 0:
            return 0.0

        return success_count / total_uses

    def get_execution_statistics(self) -> dict[str, Any]:
        """Get overall statistics about execution history."""
        if not self.memories:
            return {
                "total_executions": 0,
                "successful": 0,
                "partial": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_learning_score": 0.0,
            }

        outcomes = {"success": 0, "partial": 0, "failure": 0}
        total_learning_score = 0.0

        for memory in self.memories:
            outcomes[memory.execution_outcome] = (
                outcomes.get(memory.execution_outcome, 0) + 1
            )
            total_learning_score += memory.learning_metrics.get(
                "overall_learning_score", 0
            )

        total = len(self.memories)
        success_rate = outcomes["success"] / total if total > 0 else 0.0
        avg_learning_score = total_learning_score / total if total > 0 else 0.0

        return {
            "total_executions": total,
            "successful": outcomes["success"],
            "partial": outcomes["partial"],
            "failed": outcomes["failure"],
            "success_rate": success_rate,
            "avg_learning_score": avg_learning_score,
        }

    def get_tool_statistics(self) -> dict[str, dict[str, Any]]:
        """Get performance statistics for each tool."""
        tool_stats = {}

        for memory in self.memories:
            for tool_id, score in memory.tool_performance_scores.items():
                if tool_id not in tool_stats:
                    tool_stats[tool_id] = {
                        "uses": 0,
                        "successes": 0,
                        "total_score": 0.0,
                        "avg_score": 0.0,
                    }

                tool_stats[tool_id]["uses"] += 1
                if memory.execution_outcome in ["success", "partial"]:
                    tool_stats[tool_id]["successes"] += 1
                tool_stats[tool_id]["total_score"] += score

        # Compute averages
        for tool_id, stats in tool_stats.items():
            if stats["uses"] > 0:
                stats["avg_score"] = stats["total_score"] / stats["uses"]
                stats["win_rate"] = stats["successes"] / stats["uses"]

        return tool_stats

    def clear(self):
        """Clear all memories."""
        self.memories = []
        self.save()

    def get_memory_size(self) -> int:
        """Get number of stored memories."""
        return len(self.memories)
