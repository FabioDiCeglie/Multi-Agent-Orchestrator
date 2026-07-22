from __future__ import annotations

from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.critic import CriticAgent
from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from config.schema import OrchestratorConfig


def _build_pipeline(cfg: OrchestratorConfig, mcp_urls: list[str]) -> LoopAgent:
    return LoopAgent(
        name="orchestrator",
        max_iterations=cfg.max_iterations,
        sub_agents=[
            SequentialAgent(
                name="pipeline",
                sub_agents=[PlannerAgent(), ExecutorAgent(mcp_urls), CriticAgent()],
            )
        ],
    )


async def run(cfg: OrchestratorConfig, mcp_urls: list[str]) -> str:
    session_service = InMemorySessionService()
    runner = Runner(
        agent=_build_pipeline(cfg, mcp_urls),
        app_name="orchestrator",
        session_service=session_service,
    )
    session = await session_service.create_session(app_name="orchestrator", user_id="user")
    message = types.Content(role="user", parts=[types.Part(text=cfg.goal)])

    final = ""
    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
        if event.is_final_response() and event.content:
            final = event.content.parts[0].text
    return final
