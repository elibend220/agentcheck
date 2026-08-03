"""Agent Coordinator for full Phase 1-5 pipeline."""
from __future__ import annotations

from typing import Callable
from langgraph.graph import StateGraph, END

from agents.state import FullAgentState
from agents.phase1_nlp import make_nlp_node
from agents.phase2_knowledge import make_knowledge_node
from agents.phase3a_consciousness import make_consciousness_node
from agents.phase3b_reasoning import make_reasoning_node
from agents.phase3c_creativity import make_creativity_node
from agents.phase4a_tool_selection import make_tool_selection_node
from agents.phase4b_tool_execution import make_tool_execution_node
from agents.phase4c_tool_verification import make_tool_verification_node
from agents.phase5_quantum import make_quantum_optimization_node, make_phase5_summary_node
from agents.phase6_learning import make_learning_feedback_node, make_phase6_summary_node
from agents.phase7_memory import (
    make_memory_persistence_node,
    make_memory_retrieval_node,
    make_phase7_summary_node,
)
from agents.phase8_error_recovery import (
    make_error_detection_node,
    make_retry_orchestration_node,
    make_recovery_execution_node,
    make_recovery_summary_node,
)
from agents.phase9_explainability import (
    make_reasoning_trace_node,
    make_confidence_justification_node,
    make_decision_audit_log_node,
    make_explainability_summary_node,
)
from learning.memory_manager import MemoryManager
from tools.schema import ToolRegistry
from tools.executor import SafetyValidator

LLMFn = Callable[[str], str]


class AgentCoordinator:
    """
    Orchestrates all 9 phases:

    Phase 1: NLP (intent, entities)
    Phase 2: Knowledge (semantic retrieval)
    Phase 3a: Consciousness (attention, metacognition)
    Phase 3b: Reasoning (logical/causal analysis)
    Phase 3c: Creativity (novel ideas, analogies)
    Phase 4a: Tool Selection (choose tools)
    Phase 4b: Tool Execution (execute safely)
    Phase 4c: Tool Verification (validate results)
    Phase 5a: Quantum Optimization (superposition, entanglement, tunneling, amplification, annealing)
    Phase 5b: Quantum Summary (report quantum metrics)
    Phase 6a: Learning & Feedback Loop (analyze results, extract lessons)
    Phase 6b: Learning Summary (report insights and recommendations)
    Phase 7a: Memory Persistence (save to persistent memory)
    Phase 7b: Memory Retrieval (retrieve and synthesize historical knowledge)
    Phase 7c: Memory Summary (report memory insights)
    Phase 8a: Error Detection (identify failures)
    Phase 8b: Retry Orchestration (plan recovery)
    Phase 8c: Recovery Execution (execute recovery)
    Phase 8d: Recovery Summary (report recovery results)
    Phase 9a: Reasoning Traces (explain each phase's reasoning)
    Phase 9b: Confidence Justification (justify confidence scores)
    Phase 9c: Decision Audit Log (maintain audit trail)
    Phase 9d: Explainability Summary (report transparency metrics)
    """

    def __init__(
        self,
        llm: LLMFn,
        tool_registry: ToolRegistry = None,
        safety_validator: SafetyValidator = None,
        memory_manager: MemoryManager = None,
        enable_phase4: bool = True,
        enable_phase5: bool = True,
        enable_phase6: bool = True,
        enable_phase7: bool = True,
        enable_phase8: bool = True,
        enable_phase9: bool = True,
        dry_run_mode: bool = False,
    ):
        self.llm = llm
        self.registry = tool_registry
        self.safety_validator = safety_validator or SafetyValidator()
        self.memory_manager = memory_manager or MemoryManager()
        self.enable_phase4 = enable_phase4 and (tool_registry is not None)
        self.enable_phase5 = enable_phase5 and self.enable_phase4
        self.enable_phase6 = enable_phase6
        self.enable_phase7 = enable_phase7
        self.enable_phase8 = enable_phase8
        self.enable_phase9 = enable_phase9
        self.dry_run_mode = dry_run_mode

        self.graph = self._build_graph()

    def _build_graph(self):
        """Construct the LangGraph pipeline."""
        graph = StateGraph(FullAgentState)

        # Phase 1-3 (always included)
        graph.add_node("phase1_nlp", make_nlp_node(self.llm))
        graph.add_node("phase2_knowledge", make_knowledge_node(self.llm))
        graph.add_node("phase3a_consciousness", make_consciousness_node(self.llm))
        graph.add_node("phase3b_reasoning", make_reasoning_node(self.llm))
        graph.add_node("phase3c_creativity", make_creativity_node(self.llm))

        # Phase 4 (conditional on registry)
        if self.enable_phase4:
            graph.add_node(
                "phase4a_tool_selection",
                make_tool_selection_node(self.llm, self.registry),
            )
            graph.add_node(
                "phase4b_tool_execution",
                make_tool_execution_node(self.llm, self.registry, self.safety_validator),
            )
            graph.add_node(
                "phase4c_tool_verification",
                make_tool_verification_node(self.llm),
            )

        # Phase 5 (conditional on Phase 4)
        if self.enable_phase5:
            graph.add_node(
                "phase5a_quantum_optimization",
                make_quantum_optimization_node(self.llm, self.registry),
            )
            graph.add_node(
                "phase5b_quantum_summary",
                make_phase5_summary_node(self.llm),
            )

        # Phase 6 (always included if enabled)
        if self.enable_phase6:
            graph.add_node(
                "phase6a_learning_feedback",
                make_learning_feedback_node(self.llm),
            )
            graph.add_node(
                "phase6b_learning_summary",
                make_phase6_summary_node(self.llm),
            )

        # Phase 7 (always included if enabled)
        if self.enable_phase7:
            graph.add_node(
                "phase7a_memory_persistence",
                make_memory_persistence_node(self.llm, self.memory_manager),
            )
            graph.add_node(
                "phase7b_memory_retrieval",
                make_memory_retrieval_node(self.llm, self.memory_manager),
            )
            graph.add_node(
                "phase7c_memory_summary",
                make_phase7_summary_node(self.llm),
            )

        # Phase 8 (always included if enabled)
        if self.enable_phase8:
            graph.add_node(
                "phase8a_error_detection",
                make_error_detection_node(self.llm),
            )
            graph.add_node(
                "phase8b_retry_orchestration",
                make_retry_orchestration_node(self.llm, self.memory_manager),
            )
            graph.add_node(
                "phase8c_recovery_execution",
                make_recovery_execution_node(self.llm),
            )
            graph.add_node(
                "phase8d_recovery_summary",
                make_recovery_summary_node(self.llm),
            )

        # Phase 9 (always included if enabled)
        if self.enable_phase9:
            graph.add_node(
                "phase9a_reasoning_traces",
                make_reasoning_trace_node(self.llm),
            )
            graph.add_node(
                "phase9b_confidence_justification",
                make_confidence_justification_node(self.llm),
            )
            graph.add_node(
                "phase9c_decision_audit_log",
                make_decision_audit_log_node(self.llm),
            )
            graph.add_node(
                "phase9d_explainability_summary",
                make_explainability_summary_node(self.llm),
            )

        # Edges: sequential pipeline
        graph.set_entry_point("phase1_nlp")
        graph.add_edge("phase1_nlp", "phase2_knowledge")
        graph.add_edge("phase2_knowledge", "phase3a_consciousness")
        graph.add_edge("phase3a_consciousness", "phase3b_reasoning")
        graph.add_edge("phase3b_reasoning", "phase3c_creativity")

        if self.enable_phase4:
            graph.add_edge("phase3c_creativity", "phase4a_tool_selection")
            graph.add_edge("phase4a_tool_selection", "phase4b_tool_execution")
            graph.add_edge("phase4b_tool_execution", "phase4c_tool_verification")

            if self.enable_phase5:
                graph.add_edge("phase4c_tool_verification", "phase5a_quantum_optimization")
                graph.add_edge("phase5a_quantum_optimization", "phase5b_quantum_summary")

                if self.enable_phase6:
                    graph.add_edge("phase5b_quantum_summary", "phase6a_learning_feedback")
                    graph.add_edge("phase6a_learning_feedback", "phase6b_learning_summary")

                    if self.enable_phase7:
                        graph.add_edge("phase6b_learning_summary", "phase7a_memory_persistence")
                        graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                        graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                        if self.enable_phase8:
                            graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase7c_memory_summary", END)
                    else:
                        if self.enable_phase8:
                            graph.add_edge("phase6b_learning_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase6b_learning_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase6b_learning_summary", END)
                else:
                    if self.enable_phase7:
                        graph.add_edge("phase5b_quantum_summary", "phase7a_memory_persistence")
                        graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                        graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                        if self.enable_phase8:
                            graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase7c_memory_summary", END)
                    else:
                        if self.enable_phase8:
                            graph.add_edge("phase5b_quantum_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase5b_quantum_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase5b_quantum_summary", END)
            else:
                if self.enable_phase6:
                    graph.add_edge("phase4c_tool_verification", "phase6a_learning_feedback")
                    graph.add_edge("phase6a_learning_feedback", "phase6b_learning_summary")

                    if self.enable_phase7:
                        graph.add_edge("phase6b_learning_summary", "phase7a_memory_persistence")
                        graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                        graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                        if self.enable_phase8:
                            graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase7c_memory_summary", END)
                    else:
                        if self.enable_phase8:
                            graph.add_edge("phase6b_learning_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase6b_learning_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase6b_learning_summary", END)
                else:
                    if self.enable_phase7:
                        graph.add_edge("phase4c_tool_verification", "phase7a_memory_persistence")
                        graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                        graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                        if self.enable_phase8:
                            graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase7c_memory_summary", END)
                    else:
                        if self.enable_phase8:
                            graph.add_edge("phase4c_tool_verification", "phase8a_error_detection")
                        else:
                            if self.enable_phase9:
                                graph.add_edge("phase4c_tool_verification", "phase9a_reasoning_traces")
                            else:
                                graph.add_edge("phase4c_tool_verification", END)
        else:
            if self.enable_phase6:
                graph.add_edge("phase3c_creativity", "phase6a_learning_feedback")
                graph.add_edge("phase6a_learning_feedback", "phase6b_learning_summary")

                if self.enable_phase7:
                    graph.add_edge("phase6b_learning_summary", "phase7a_memory_persistence")
                    graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                    graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                    if self.enable_phase8:
                        graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                    else:
                        if self.enable_phase9:
                            graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                        else:
                            graph.add_edge("phase7c_memory_summary", END)
                else:
                    if self.enable_phase8:
                        graph.add_edge("phase6b_learning_summary", "phase8a_error_detection")
                    else:
                        if self.enable_phase9:
                            graph.add_edge("phase6b_learning_summary", "phase9a_reasoning_traces")
                        else:
                            graph.add_edge("phase6b_learning_summary", END)
            else:
                if self.enable_phase7:
                    graph.add_edge("phase3c_creativity", "phase7a_memory_persistence")
                    graph.add_edge("phase7a_memory_persistence", "phase7b_memory_retrieval")
                    graph.add_edge("phase7b_memory_retrieval", "phase7c_memory_summary")

                    if self.enable_phase8:
                        graph.add_edge("phase7c_memory_summary", "phase8a_error_detection")
                    else:
                        if self.enable_phase9:
                            graph.add_edge("phase7c_memory_summary", "phase9a_reasoning_traces")
                        else:
                            graph.add_edge("phase7c_memory_summary", END)
                else:
                    if self.enable_phase8:
                        graph.add_edge("phase3c_creativity", "phase8a_error_detection")
                    else:
                        if self.enable_phase9:
                            graph.add_edge("phase3c_creativity", "phase9a_reasoning_traces")
                        else:
                            graph.add_edge("phase3c_creativity", END)

        # Phase 8 edges (if enabled)
        if self.enable_phase8:
            graph.add_edge("phase8a_error_detection", "phase8b_retry_orchestration")
            graph.add_edge("phase8b_retry_orchestration", "phase8c_recovery_execution")
            graph.add_edge("phase8c_recovery_execution", "phase8d_recovery_summary")

            if self.enable_phase9:
                graph.add_edge("phase8d_recovery_summary", "phase9a_reasoning_traces")
            else:
                graph.add_edge("phase8d_recovery_summary", END)

        # Phase 9 edges (if enabled)
        if self.enable_phase9:
            graph.add_edge("phase9a_reasoning_traces", "phase9b_confidence_justification")
            graph.add_edge("phase9b_confidence_justification", "phase9c_decision_audit_log")
            graph.add_edge("phase9c_decision_audit_log", "phase9d_explainability_summary")
            graph.add_edge("phase9d_explainability_summary", END)

        return graph.compile()

    def invoke(self, input_state: FullAgentState) -> FullAgentState:
        """Execute the full pipeline."""
        input_state["dry_run_mode"] = self.dry_run_mode
        return self.graph.invoke(input_state)
