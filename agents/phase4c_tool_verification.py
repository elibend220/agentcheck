"""Phase 4c: Tool Verification Agent."""
from __future__ import annotations

from typing import Callable
from agents.state import FullAgentState, ToolVerificationResult

LLMFn = Callable[[str], str]

VERIFICATION_PROMPT = """You are verifying tool execution results for consistency and hallucination detection.

Tool executed: {tool_name}
Result: {result_value}
Result type: {result_type}

Original state context:
- Intent: {intent}
- Reasoning: {reasoning_conclusion}
- Prior knowledge: {knowledge_summary}
- Attention: {attention_focus}

Check for:
1. Hallucinations (is result plausible given inputs?)
2. Consistency (does result match prior reasoning/knowledge?)
3. Type correctness (is result the expected type?)
4. Reasonableness (is magnitude/scale appropriate?)

Respond in exact format:
VALID: true or false
CONFIDENCE: <0.0 to 1.0>
CONCERNS: <comma-separated list of issues, or "none">
REASONING: <brief explanation>
"""


def make_tool_verification_node(llm: LLMFn):
    """
    Creates a node that verifies tool execution results.

    - Detects hallucinations
    - Validates consistency with state
    - Provides confidence scores
    - Flags uncertainties
    """

    def verify_tools(state: FullAgentState) -> FullAgentState:
        execution_results = state.get("tool_execution_results", [])
        verification_results = []
        verified_results = []

        for exec_result in execution_results:
            # Skip failed executions (already invalid)
            if not exec_result.success:
                verification_results.append(
                    ToolVerificationResult(
                        tool_id=exec_result.tool_id,
                        valid=False,
                        concerns=["Tool execution failed"],
                        confidence=1.0,
                        reasoning="Execution failed",
                    )
                )
                continue

            # Get tool name for reporting
            tool_name = exec_result.tool_id.split(".")[-1]

            # Verify successful result
            prompt = VERIFICATION_PROMPT.format(
                tool_name=tool_name,
                result_value=str(exec_result.value)[:100],
                result_type=type(exec_result.value).__name__,
                intent=state.get("intent", ""),
                reasoning_conclusion=state.get("reasoning_conclusion", "")[:100],
                knowledge_summary=state.get("knowledge_summary", "")[:100],
                attention_focus=", ".join(state.get("attention_focus", [])),
            )

            response = llm(prompt).strip()
            verification = _parse_verification_response(response, exec_result.tool_id)
            verification_results.append(verification)

            # Track verified results
            if verification.valid:
                verified_results.append(exec_result.value)

        return {
            "verification_results": verification_results,
            "verified_results": verified_results,
        }

    return verify_tools


def _parse_verification_response(response: str, tool_id: str) -> ToolVerificationResult:
    """Parse verification response from LLM."""
    valid = True
    confidence = 0.5
    concerns = []
    reasoning = response

    for line in response.splitlines():
        line = line.strip()

        if line.startswith("VALID:"):
            valid_str = line.split(":", 1)[1].strip().lower()
            valid = valid_str in ["true", "yes", "valid"]

        elif line.startswith("CONFIDENCE:"):
            try:
                confidence = float(line.split(":", 1)[1].strip())
                confidence = max(0.0, min(1.0, confidence))
            except ValueError:
                pass

        elif line.startswith("CONCERNS:"):
            concerns_str = line.split(":", 1)[1].strip()
            if concerns_str.lower() != "none":
                concerns = [c.strip() for c in concerns_str.split(",") if c.strip()]

        elif line.startswith("REASONING:"):
            reasoning = line.split(":", 1)[1].strip()

    return ToolVerificationResult(
        tool_id=tool_id, valid=valid, concerns=concerns, confidence=confidence, reasoning=reasoning
    )
