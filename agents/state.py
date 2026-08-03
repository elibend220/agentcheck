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

    # === Phase 11: Proactive Personal Assistant ===
    user_profile: dict[str, Any]
    user_status: str
    user_preferences: dict[str, Any]
    user_patterns: list[str]
    predicted_needs: list[str]
    proactive_suggestions: list[str]
    anticipation_confidence: float
    priority_actions: list[str]
    autonomous_actions: list[str]
    action_priorities: list[str]
    action_risks: list[str]
    requires_confirmation: bool
    assistant_ready: bool
    phase11_summary: str

    # === Phase 12: Multi-Channel Communication & External Tool Integration ===
    active_channels: list[str]
    channel_configs: dict[str, Any]
    connection_status: dict[str, str]
    channel_readiness: float
    message_queue: list[dict[str, Any]]
    routing_rules: dict[str, Any]
    channel_contexts: dict[str, Any]
    routing_confidence: float
    external_tools: list[str]
    tool_connections: dict[str, Any]
    available_integrations: list[str]
    tool_bridge_ready: bool
    tool_capabilities: dict[str, Any]
    multichannel_ready: bool
    phase12_summary: str

    # === Phase 13: Dynamic Plugin System & Autonomous Integration Discovery ===
    discovered_plugins: list[str]
    plugin_suggestions: list[str]
    missing_integrations: list[str]
    discovery_confidence: float
    built_plugins: list[str]
    plugin_specifications: dict[str, Any]
    plugin_templates: dict[str, Any]
    builder_ready: bool
    plugin_build_confidence: float
    installed_plugins: list[str]
    plugin_status: dict[str, str]
    installation_log: list[str]
    installer_ready: bool
    installation_confidence: float
    manual_plugin_requests: list[str]
    plugin_system_ready: bool
    phase13_summary: str

    # === Phase 14: Real-Time Event Streaming & Continuous Monitoring ===
    event_streams: list[str]
    monitored_sources: list[str]
    listener_status: str
    listener_ready: bool
    streaming_confidence: float
    processed_events: list[str]
    event_queue: list[str]
    triggered_actions: list[str]
    event_processing_confidence: float
    realtime_responses: list[str]
    response_latency_ms: int
    response_queue: list[str]
    response_confidence: float
    realtime_streaming_ready: bool
    phase14_summary: str

    # === Phase 15: Emotional Intelligence & Sentiment Analysis ===
    user_sentiment: str
    sentiment_score: float
    emotional_tone: list[str]
    sentiment_confidence: float
    detected_emotions: list[str]
    emotion_intensities: dict[str, float]
    emotional_state: str
    emotion_detection_confidence: float
    empathetic_response: str
    response_tone_adjustment: str
    emotional_support_level: float
    empathy_confidence: float
    emotional_intelligence_ready: bool
    phase15_summary: str

    # === Phase 21: Voice & Natural Conversation Interface ===
    speech_detected: bool
    transcribed_text: str
    speech_confidence: float
    speech_tone: str
    voice_characteristics: dict[str, Any]
    conversation_context: dict[str, Any]
    conversation_flow: list[str]
    natural_pauses: list[str]
    interruption_points: list[str]
    conversation_confidence: float
    spoken_response: str
    speech_rate: int
    prosody_markers: list[str]
    emphasis_points: list[str]
    tts_ready: bool
    tts_confidence: float
    voice_interface_ready: bool
    phase21_summary: str

    # === Phase 16: System Engineering & Self-Optimization ===
    phase_latencies: dict[str, float]
    phase_success_rates: dict[str, float]
    node_execution_counts: dict[str, int]
    resource_usage: dict[str, Any]
    bottleneck_phases: list[str]
    metrics_collection_confidence: float
    critical_phases: list[str]
    low_impact_phases: list[str]
    phase_coupling_analysis: dict[str, Any]
    optimization_opportunities: list[str]
    architecture_analysis_confidence: float
    recommended_phase_changes: list[str]
    recommended_routing_changes: list[str]
    recommended_resource_allocation: dict[str, Any]
    optimization_priority: list[str]
    optimization_recommendation_confidence: float
    applied_optimizations: list[str]
    optimization_applied: bool
    system_optimized: bool
    optimization_applied_confidence: float
    phase16_summary: str

    # === Phase 17: Constitutional Framework & Values Alignment ===
    core_mission: str
    core_values: list[str]
    foundational_principles: list[str]
    mission_definition_confidence: float
    value_alignment_score: float
    alignment_violations: list[str]
    alignment_recommendations: list[str]
    value_alignment_confidence: float
    enforced_constraints: list[str]
    blocked_changes: list[str]
    constraint_violations_detected: bool
    constraint_enforcement_confidence: float
    constitutional_framework_established: bool
    alignment_compliant: bool
    framework_confidence: float
    phase17_summary: str

    # === Phase 18: Safety & Mutation Prevention ===
    detected_mutations: list[str]
    mutation_risk_level: str
    risky_modifications: list[str]
    mutation_analysis_confidence: float
    safety_checks_passed: bool
    safety_violations: list[str]
    quarantined_changes: list[str]
    safety_validation_confidence: float
    rollback_checkpoint_created: bool
    rollback_procedures: list[str]
    recovery_snapshots: list[str]
    rollback_manager_confidence: float
    integrity_check_passed: bool
    system_protected: bool
    mutation_prevention_active: bool
    system_integrity_confidence: float
    phase18_summary: str

    # === Phase 19: Personality & Conversational Charm ===
    personality_traits: list[str]
    character_voice: str
    humor_level: float
    formality_level: float
    charm_score: float
    personality_confidence: float
    conversational_response: str
    response_wit_level: float
    response_charm_applied: float
    natural_dialogue_confidence: float
    user_quirks: list[str]
    user_preferences_learned: dict[str, Any]
    relationship_depth: float
    personalization_level: float
    relationship_confidence: float
    personality_established: bool
    character_ready: bool
    conversational_charm_active: bool
    phase19_summary: str

    # === Phase 20: Proactive Risk Assessment & Intelligent Refusal ===
    predicted_consequences: list[str]
    identified_risks: list[str]
    risk_severity: str
    harm_assessment: float
    second_order_effects: list[str]
    third_order_effects: list[str]
    consequence_confidence: float
    risk_warning: str
    risk_explanation: str
    alternative_approaches: list[str]
    negotiation_points: list[str]
    risk_communication_confidence: float
    should_refuse: bool
    refusal_reasoning: str
    refusal_dialogue: str
    alternative_suggestions: list[str]
    concern_expression: str
    intelligent_refusal_confidence: float
    negotiation_possible: bool
    compromise_options: list[str]
    ethical_explanation: str
    trust_building_response: str
    negotiation_confidence: float
    phase20_summary: str

    # === Cross-cutting ===
    execution_history: list[dict]
    dry_run_mode: bool
    safety_flags: list[str]
    error_log: list[str]
    source_name: str
    credibility_score: int
    credibility_rationale: str
