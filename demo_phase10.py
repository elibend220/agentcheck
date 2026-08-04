#!/usr/bin/env python3
"""
Demonstration of Phase 10: Autonomous Planning & Goal Decomposition.

Shows full 1-10 pipeline with goal decomposition, plan generation, verification, and risk analysis.
"""

import tempfile
from agents.state import FullAgentState
from agents.coordinator import AgentCoordinator
from tools.builtin import create_builtin_registry
from tools.executor import SafetyValidator
from learning.memory_manager import MemoryManager


class DemoLLMPhase10:
    """LLM for demonstration with planning-focused responses."""

    def __init__(self):
        self.call_count = 0

    def __call__(self, prompt: str) -> str:
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Phases 1-9 responses
        if "extract" in prompt_lower and "intent" in prompt_lower:
            return """INTENT: Launch new machine learning product
ENTITIES: ML system, product launch, deployment
SUMMARY: Develop and deploy machine learning system"""

        if "knowledge" in prompt_lower:
            return """KNOWLEDGE_POINTS: ML development lifecycle, deployment best practices
KNOWLEDGE_SUMMARY: Knowledge available on ML systems and deployment"""

        if "attention" in prompt_lower or "metacognitive" in prompt_lower:
            return """ATTENTION_FOCUS: model quality, scalability, reliability
METACOGNITIVE_NOTES: Complex system requiring careful planning"""

        if "reasoning" in prompt_lower:
            return """REASONING_TYPE: systematic
CAUSAL: Good planning leads to successful deployment
LOGICAL: Sequential development approach required
CONCLUSION: Structured planning essential"""

        if "creative" in prompt_lower:
            return """CREATIVE_IDEAS: Modular architecture, CI/CD pipeline, A/B testing
NOVELTY_SCORE: 74"""

        if "select which tools" in prompt_lower or "available tools" in prompt_lower:
            return """SELECTED_TOOLS: data.process, ml.train, deploy.verify
CONFIDENCE: 0.90"""

        if "verif" in prompt_lower or "valid:" in prompt_lower:
            return "VALID: true\nCONFIDENCE: 0.91"

        # Phase 9 responses (abbreviated)
        if "reasoning trace" in prompt_lower or "explain" in prompt_lower:
            return "SUMMARY: Reasoning trace\nREASONING: Systematic approach"

        # Phase 10a: Goal Decomposition
        if "decompose" in prompt_lower or "subgoal" in prompt_lower:
            return """PRIMARY_GOAL: Launch ML product with >95% uptime
SUBGOALS:
  1. Prepare data pipeline and ensure quality
  2. Train and validate ML model
  3. Build deployment infrastructure
  4. Implement monitoring and logging
  5. Execute production deployment
  6. Monitor and optimize performance
HIERARCHY: Prerequisites must complete before dependent phases
DEPENDENCIES: Training depends on data prep, deployment depends on infra"""

        # Phase 10b: Plan Generation
        if "execution plan" in prompt_lower or "step-by-step" in prompt_lower:
            return """EXECUTION_STEPS:
  Step 1: Set up data infrastructure (Week 1-2)
  Step 2: Collect and validate training data (Week 2-4)
  Step 3: Develop and train ML model (Week 4-8)
  Step 4: Validate model performance (Week 8-9)
  Step 5: Build deployment pipeline (Week 6-8, parallel)
  Step 6: Deploy to staging (Week 9)
  Step 7: Production deployment (Week 10)
  Step 8: Monitor and optimize (Week 10+)
CRITICAL_PATH: Data Prep → Training → Validation → Production Deployment
ESTIMATED_DURATION: 10
RESOURCE_REQUIREMENTS:
  - Data Engineers: 2
  - ML Engineers: 3
  - DevOps Engineers: 2
  - Infrastructure: High-performance compute
PARALLELIZABLE: Deployment pipeline setup can run parallel with training"""

        # Phase 10c: Plan Verification
        if "verify" in prompt_lower and ("feasibility" in prompt_lower or "plan" in prompt_lower):
            return """FEASIBILITY: 0.82
RISKS:
  1. Data quality issues delaying training
  2. Model performance missing targets
  3. Infrastructure scalability challenges
  4. Resource allocation conflicts
  5. Timeline compression risks
CONTINGENCIES:
  1. Pre-stage additional training data
  2. Lower initial performance targets
  3. Plan infrastructure redundancy
  4. Cross-train team members
  5. Compress non-critical phases
VALID: true
CONFIDENCE: 0.81"""

        return "DEFAULT: continue"


def main():
    """Run full Phase 1-10 demonstration with planning."""
    print("=" * 100)
    print("PHASE 10: AUTONOMOUS PLANNING & GOAL DECOMPOSITION - FULL 1-10 PIPELINE DEMONSTRATION")
    print("=" * 100)

    # Create memory manager
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        memory_path = f.name

    memory_manager = MemoryManager(memory_path)

    # Create coordinator with all 10 phases enabled
    print("\n[Setup] Enabling all phases 1-10 with autonomous planning...")
    llm = DemoLLMPhase10()
    registry = create_builtin_registry()
    safety_validator = SafetyValidator()

    coordinator = AgentCoordinator(
        llm=llm,
        tool_registry=registry,
        safety_validator=safety_validator,
        memory_manager=memory_manager,
        enable_phase4=True,
        enable_phase5=True,
        enable_phase6=True,
        enable_phase7=True,
        enable_phase8=True,
        enable_phase9=True,
        enable_phase10=True,
        dry_run_mode=True,
    )

    # Execute planning task
    print("\n" + "=" * 100)
    print("FULL 1-10 PIPELINE EXECUTION: ML Product Launch Planning")
    print("=" * 100)

    initial_state: FullAgentState = {
        "input_text": "Plan the launch of our new machine learning product with high reliability requirements",
        "tool_selection_confidence": 0.90,
    }

    print(f"\nInput Task: {initial_state['input_text']}")
    print("\nExecuting all 10 phases...")

    result = coordinator.invoke(initial_state)

    # Display Results
    print("\n" + "=" * 100)
    print("PHASE RESULTS SUMMARY")
    print("=" * 100)

    print("\n[Phases 1-9] Cognitive & Analytical Phases:")
    print(f"  Intent: {result.get('intent', 'N/A')[:60]}...")
    print(f"  Lessons Learned: {len(result.get('lessons_learned', []))} insights")
    print(f"  Explainability Score: {result.get('explainability_score', 0):.1%}")

    # Planning Results
    print("\n" + "=" * 100)
    print("PHASE 10: AUTONOMOUS PLANNING RESULTS")
    print("=" * 100)

    # Goal Decomposition
    print("\n[10a] Goal Decomposition:")
    print(f"  Primary Goal: {result.get('primary_goal', 'N/A')[:70]}...")
    subgoals = result.get("subgoals", [])
    print(f"  Subgoals ({len(subgoals)}):")
    for i, subgoal in enumerate(subgoals[:5], 1):
        print(f"    {i}. {subgoal}")

    # Execution Plan
    print("\n[10b] Execution Plan:")
    plan_steps = result.get("plan_steps", 0)
    print(f"  Total Steps: {plan_steps}")
    print(f"  Estimated Duration: {result.get('plan_estimated_duration', 0)} weeks")

    critical_path = result.get("critical_path", [])
    if critical_path:
        print(f"  Critical Path ({len(critical_path)} steps):")
        for step in critical_path[:5]:
            print(f"    → {step}")

    # Resource Requirements
    resources = result.get("plan_resource_requirements", {})
    if resources:
        print(f"  Resource Requirements:")
        for resource, details in list(resources.items())[:3]:
            print(f"    • {resource}: {str(details)[:50]}...")

    # Plan Verification
    print("\n[10c] Plan Verification:")
    print(f"  Feasibility Score: {result.get('plan_feasibility', 0):.2%}")
    print(f"  Plan Valid: {'✓ YES' if result.get('plan_valid') else '✗ NO'}")
    print(f"  Verification Confidence: {result.get('verification_confidence', 0):.2f}")

    # Risks
    risks = result.get("plan_risks", [])
    if risks:
        print(f"\n  Identified Risks ({len(risks)}):")
        for risk in risks[:5]:
            print(f"    ⚠ {risk}")

    # Contingencies
    contingencies = result.get("contingencies", [])
    if contingencies:
        print(f"\n  Contingency Plans ({len(contingencies)}):")
        for cont in contingencies[:5]:
            print(f"    • {cont}")

    # Planning Summary
    print("\n[10d] Planning Summary:")
    print(result.get("phase10_summary", "N/A"))

    # Statistics
    print("\n" + "=" * 100)
    print("EXECUTION STATISTICS")
    print("=" * 100)
    print(f"Total LLM Calls: {llm.call_count}")
    print(f"Total Phases Executed: 10")
    print(f"Subgoals Identified: {len(subgoals)}")
    print(f"Plan Steps: {plan_steps}")
    print(f"Critical Path Length: {len(critical_path)}")
    print(f"Identified Risks: {len(risks)}")
    print(f"Contingency Plans: {len(contingencies)}")
    print(f"Plan Feasibility: {result.get('plan_feasibility', 0):.1%}")

    # Key Insights
    print("\n" + "=" * 100)
    print("KEY PLANNING INSIGHTS")
    print("=" * 100)
    print("""
✓ Phase 10 provides autonomous multi-step planning capabilities
✓ Goal decomposition breaks complex tasks into manageable subgoals
✓ Plan generation creates detailed execution roadmaps
✓ Risk identification highlights potential challenges
✓ Contingency planning enables adaptive execution

Complete 10-Phase AGI Framework:
  1. NLP → 2. Knowledge → 3a. Consciousness → 3b. Reasoning → 3c. Creativity
  4. Tools → 5. Quantum → 6. Learning → 7. Memory → 8. Error Recovery
  9. Explainability → 10. Autonomous Planning

This 10-phase system provides:
  • Cognitive understanding and reasoning
  • Conscious decision-making
  • Quantum-inspired optimization
  • Continuous learning
  • Explainable decisions
  • Autonomous planning and execution
    """)

    # Cleanup
    import os
    if os.path.exists(memory_path):
        os.remove(memory_path)

    print("\n" + "=" * 100)
    print("DEMONSTRATION COMPLETE - 10-PHASE AGI SYSTEM FULLY OPERATIONAL")
    print("=" * 100)


if __name__ == "__main__":
    main()
