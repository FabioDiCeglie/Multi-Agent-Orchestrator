from google.adk.agents import LlmAgent

INSTRUCTION = """You are a planning agent. Given a high-level goal, break it down into a short list of concrete subtasks.

Return a numbered markdown list — nothing else. Keep it minimal: 2 to 5 subtasks.

Example:
1. Search for the top 5 open-source LLM frameworks
2. Compare them by GitHub stars, license, and Python support
3. Write a markdown comparison table

If you receive feedback from a previous attempt, use it to improve the plan.
"""


class PlannerAgent(LlmAgent):
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        super().__init__(
            name="planner",
            model=model,
            instruction=INSTRUCTION,
        )
