from __future__ import annotations

import re
from typing import Any

from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.critic import CriticAgent
from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.summarizer import SummarizerAgent
from config.schema import OrchestratorConfig
from models.context_file import ContextFile


class BaseOrchestrator:
    def __init__(
        self,
        cfg: OrchestratorConfig,
        mcp_urls: list[str],
        files: list[ContextFile] | None = None,
    ) -> None:
        self.cfg = cfg
        self.mcp_urls = mcp_urls
        self.files = files or []
        self.iteration = 0
        self.summary_text = ""

    def _build_pipeline(self) -> SequentialAgent:
        return SequentialAgent(
            name="orchestrator",
            sub_agents=[
                LoopAgent(
                    name="planning_loop",
                    max_iterations=self.cfg.max_iterations,
                    sub_agents=[
                        SequentialAgent(
                            name="pipeline",
                            sub_agents=[
                                PlannerAgent(),
                                ExecutorAgent(self.mcp_urls, self.files),
                                CriticAgent(),
                            ],
                        )
                    ],
                ),
                SummarizerAgent(),
            ],
        )

    def _build_prompt(self) -> str:
        if not self.files:
            return self.cfg.goal
        names = ", ".join(f.name for f in self.files)
        return (
            f"## Available Context Files\n"
            f"{names}\n\n"
            f"Use the read_context_file tool to read them.\n\n"
            f"## Goal\n{self.cfg.goal}"
        )

    async def _create_runner(self) -> tuple[Runner, Any]:
        session_service = InMemorySessionService()
        runner = Runner(
            agent=self._build_pipeline(),
            app_name="orchestrator",
            session_service=session_service,
        )
        session = await session_service.create_session(
            app_name="orchestrator", user_id="user",
        )
        return runner, session

    def _build_message(self) -> types.Content:
        return types.Content(
            role="user",
            parts=[types.Part(text=self._build_prompt())],
        )

    @staticmethod
    def clean_executor(text: str) -> str:
        text = re.sub(
            r"<search[\s\S]*?</search>", "", text, flags=re.IGNORECASE,
        )
        return re.sub(r"<[^>]+>", "", text).strip()

    @staticmethod
    def extract_tool_calls(parts: list) -> list[str]:
        return [
            p.function_call.name
            for p in parts
            if getattr(p, "function_call", None)
        ]

    @staticmethod
    def extract_tool_calls_detailed(parts: list) -> list[dict[str, Any]]:
        return [
            {"name": p.function_call.name, "args": dict(p.function_call.args)}
            for p in parts
            if getattr(p, "function_call", None)
        ]
