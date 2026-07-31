from config.schema import DEFAULT_MODEL
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.tool_context import ToolContext

INSTRUCTION = """You are a critic agent. Review the work done by the executor and decide if the goal has been achieved.

Give your verdict:
- If the goal is fully achieved: write `VERDICT: APPROVED` and then IMMEDIATELY call the `exit_loop` tool.
- If more work is needed: write `VERDICT: REVISE` followed by a short bullet list of what to fix.

Be concise. Focus on what matters for the goal.
"""


def exit_loop(tool_context: ToolContext) -> dict:
    """Call this when the work is approved to stop the loop."""
    tool_context.actions.escalate = True
    return {}


class CriticAgent(LlmAgent):
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        super().__init__(
            name="critic",
            model=LiteLlm(model=model),
            instruction=INSTRUCTION,
            tools=[exit_loop],
        )
