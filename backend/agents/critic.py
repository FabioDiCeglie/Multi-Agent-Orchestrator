from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

INSTRUCTION = """You are a critic agent. Review the work done by the executor and decide if the goal has been achieved.

End your response with one of these two lines — nothing else after it:
- `VERDICT: APPROVED` — if the goal is fully achieved
- `VERDICT: REVISE` — if more work is needed, followed by a short bullet list of what to fix

Be concise. Focus on what matters for the goal.
"""


def _check_verdict(callback_context: CallbackContext) -> types.Content | None:
    session = callback_context.session
    for event in reversed(session.events):
        if event.author == "critic" and event.content:
            for part in event.content.parts:
                if part.text and "VERDICT: APPROVED" in part.text:
                    callback_context.actions.escalate = True
            break
    return None


class CriticAgent(LlmAgent):
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        super().__init__(
            name="critic",
            model=LiteLlm(model=model),
            instruction=INSTRUCTION,
            after_agent_callback=_check_verdict,
        )
