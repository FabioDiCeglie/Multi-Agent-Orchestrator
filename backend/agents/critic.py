from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

INSTRUCTION = """You are a critic agent. Review the work done by the executor and decide if the goal has been achieved.

End your response with one of these two lines — nothing else after it:
- `VERDICT: APPROVED` — if the goal is fully achieved
- `VERDICT: REVISE` — if more work is needed, followed by a short bullet list of what to fix

Be concise. Focus on what matters for the goal.
"""


def _check_verdict(callback_context: CallbackContext) -> types.Content | None:
    session = callback_context.session
    # Walk events in reverse to find the critic's last model response
    for event in reversed(session.events):
        if event.author == "critic" and event.content:
            for part in event.content.parts:
                if part.text and "VERDICT: APPROVED" in part.text:
                    callback_context.actions.escalate = True
            break
    return None


def create_critic(model: str = "gemini-2.5-flash") -> LlmAgent:
    return LlmAgent(
        name="critic",
        model=model,
        instruction=INSTRUCTION,
        after_agent_callback=_check_verdict,
    )
