from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from config.schema import DEFAULT_MODEL

INSTRUCTION = """You are a summarization agent. The Planner, Executor and Critic have already
finished and approved the work for the user's goal.

Read everything the Executor produced and output ONLY the final, polished answer to the original
goal — nothing else.

Rules:
- Do not narrate the process: no subtask labels, no mention of tools/searches, no reasoning.
- Prefer a compact markdown table or a tight bullet list over prose.
- Be as short as possible while keeping every fact that matters.
- No preamble like "Here is the summary" — start directly with the answer.
"""


class SummarizerAgent(LlmAgent):
    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        super().__init__(
            name="summarizer",
            model=LiteLlm(model=model),
            instruction=INSTRUCTION,
        )
