"""Unified state schema for all pipeline phases (1-4)."""
from __future__ import annotations

from typing import TypedDict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToolParameter:
    """Describes a single parameter to a tool."""
    name: str
    type: str                    # "string", "int", "float", "bool", "list", "dict"
    description: str
    required: bool = True
    default: Optional[Any] = None
    enum_values: Optional[list[str]] = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Returns (is_valid, error_message)."""
        if value is None:
            if self.required and self.default is None:
                return False, f"Required parameter {self.name} is None"
            return True, None

        # Type checking
        type_map = {
            "string": str,
            "int": int,
            "float": (int, float),
            "bool": bool,
            "list": list,
            "dict": dict,
        }

        expected_type = type_map.get(self.type)
        if expected_type and not isinstance(value, expected_type):
            return False, f"Expected {self.type}, got {type(value).__name__}"

        # Enum validation
        if self.enum_values and value not in self.enum_values:
            return False, f"Value {value} not in allowed values: {self.enum_values}"

        return True, None


@dataclass
class ToolSchema:
    """Complete tool definition."""
    id: str                      # unique, e.g., "math.add", "web.search"
    name: str                    # human-readable, e.g., "Add Numbers"
    description: str             # what it does
    category: str                # "math", "text", "web", "data", "logic", "custom"
    parameters: list[ToolParameter]
    return_type: str             # "string", "int", "float", "bool", "list", "dict"
    example_usage: dict          # {"param_name": example_value, ...}

    # Safety/control
    requires_confirmation: bool = False
    requires_network: bool = False
    max_execution_time_seconds: float = 5.0

    # Metadata for agent selection
    capabilities: list[str] = None
    preconditions: list[str] = None
    example_input: dict = None
    example_output: Any = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.preconditions is None:
            self.preconditions = []
        if self.example_input is None:
            self.example_input = {}

    def __hash__(self):
        return hash(self.id)


@dataclass
class ToolExecutionResult:
    """Result of a single tool execution."""
    tool_id: str
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    confidence: float = 1.0
    safety_violations: list[str] = None

    def __post_init__(self):
        if self.safety_violations is None:
            self.safety_violations = []


@dataclass
class ToolVerificationResult:
    """Result of verifying a tool's output."""
    tool_id: str
    valid: bool
    concerns: list[str] = None
    confidence: float = 0.5
    reasoning: str = ""

    def __post_init__(self):
        if self.concerns is None:
            self.concerns = []


class FullAgentState(TypedDict, total=False):
    """Extended AgentState for full pipeline (Phases 1-4)."""

    # === Input ===
    input_text: str

    # === Phase 1: NLP ===
    intent: str
    entities: dict[str, Any]
    summary: str

    # === Phase 2: Knowledge ===
    relevant_knowledge: list[str]
    knowledge_summary: str

    # === Phase 3a: Consciousness ===
    attention_focus: list[str]
    metacognitive_notes: str

    # === Phase 3b: Reasoning ===
    reasoning_type: str
    reasoning_steps: list[str]
    reasoning_conclusion: str

    # === Phase 3c: Creativity ===
    creative_ideas: list[str]
    analogies: list[str]
    novel_combinations: list[str]

    # === Phase 4a: Tool Selection ===
    available_tools: list[ToolSchema]
    selected_tools: list[str]
    tool_selection_reasoning: str
    tool_selection_confidence: float

    # === Phase 4b: Tool Execution ===
    tool_parameters: dict[str, Any]
    tool_execution_results: list[ToolExecutionResult]

    # === Phase 4c: Tool Verification ===
    verification_results: list[ToolVerificationResult]
    verified_results: list[Any]

    # === Phase 5: Quantum Optimization ===
    quantum_state_created: bool
    quantum_amplitudes: dict[str, float]
    quantum_entanglement_matrix: dict[str, dict[str, float]]
    quantum_tunneling_solutions: list[dict]
    quantum_metrics: dict[str, float]
    quantum_optimized_tools: list[str]
    quantum_entropy: float
    quantum_purity: float
    phase5_summary: str

    # === Phase 6: Learning & Feedback Loop ===
    execution_outcome: str  # "success", "partial", "failure"
    outcome_confidence: float
    lessons_learned: list[str]
    tool_performance_scores: dict[str, float]
    phase_performance_scores: dict[str, float]
    improvement_suggestions: list[str]
    effective_tool_combinations: list[list[str]]
    failure_analysis: dict[str, Any]
    learning_metrics: dict[str, float]
    phase6_summary: str

    # === Phase 7: Persistent Memory & Knowledge Integration ===
    memory_persisted: bool
    memory_size: int
    similar_past_executions: int
    historical_lessons: list[str]
    historical_best_tools: list[str]
    historical_suggestions: list[str]
    best_tool_combinations: list[dict[str, Any]]
    execution_statistics: dict[str, Any]
    tool_statistics: dict[str, dict[str, Any]]
    common_lessons: list[tuple[str, int]]
    high_confidence_suggestions: list[str]
    phase7_synthesis: str
    phase7_insights: list[str]
    phase7_confidence: float
    phase7_recommended_approach: str
    phase7_summary: str

    # === Phase 8: Error Recovery & Intelligent Retry ===
    recovery_needed: bool
    recovery_strategy: str  # "alternative_tools", "adjust_parameters", "enhance_reasoning", etc.
    error_details: dict[str, Any]
    retry_attempted: bool
    retry_plan: dict[str, Any]
    historical_alternatives: dict[str, Any]
    retry_reasoning: str
    recovery_executed: bool
    retry_result: dict[str, Any]
    retry_success: bool
    retry_outcome: str  # "success", "partial", "failure"
    recovery_confidence: float
    recovery_attempt_count: int
    phase8_summary: str

    # === Phase 9: Explainability & Interpretability ===
    reasoning_traces: dict[str, dict[str, Any]]
    confidence_justifications: dict[str, dict[str, Any]]
    decision_audit_log: list[dict[str, Any]]
    overall_system_confidence: float
    explainability_score: float
    phase9_summary: str

    # === Phase 10: Autonomous Planning & Goal Decomposition ===
    primary_goal: str
    subgoals: list[str]
    goal_hierarchy: dict[str, Any]
    execution_plan: list[str]
    plan_steps: int
    critical_path: list[str]
    plan_estimated_duration: int
    plan_resource_requirements: dict[str, Any]
    plan_feasibility: float
    plan_risks: list[str]
    contingencies: list[str]
    plan_valid: bool
    verification_confidence: float
    phase10_summary: str

    # === Cross-cutting ===
    execution_history: list[dict]
    dry_run_mode: bool
    safety_flags: list[str]
    error_log: list[str]
    source_name: str
    credibility_score: int
    credibility_rationale: str
