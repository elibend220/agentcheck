"""Agent Coordinator for full Phase 1-4 pipeline."""
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
from tools.schema import ToolRegistry
from tools.executor import SafetyValidator

LLMFn = Callable[[str], str]


class AgentCoordinator:
    """
    Orchestrates all 4 phases:

    Phase 1: NLP (intent, entities)
    Phase 2: Knowledge (semantic retrieval)
    Phase 3a: Consciousness (attention, metacognition)
    Phase 3b: Reasoning (logical/causal analysis)
    Phase 3c: Creativity (novel ideas, analogies)
    Phase 4a: Tool Selection (choose tools)
    Phase 4b: Tool Execution (execute safely)
    Phase 4c: Tool Verification (validate results)
    """

    def __init__(
        self,
        llm: LLMFn,
        tool_registry: ToolRegistry = None,
        safety_validator: SafetyValidator = None,
        enable_phase4: bool = True,
        dry_run_mode: bool = False,
    ):
        self.llm = llm
        self.registry = tool_registry
        self.safety_validator = safety_validator or SafetyValidator()
        self.enable_phase4 = enable_phase4 and (tool_registry is not None)
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
            graph.add_edge("phase4c_tool_verification", END)
        else:
            graph.add_edge("phase3c_creativity", END)

        return graph.compile()

    def invoke(self, input_state: FullAgentState) -> FullAgentState:
        """Execute the full pipeline."""
        input_state["dry_run_mode"] = self.dry_run_mode
        return self.graph.invoke(input_state)
