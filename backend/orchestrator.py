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


import re


def _clean_executor(text: str) -> str:
    """Strip <search>...</search> XML blocks, keep only the result content."""
    text = re.sub(r"<search[\s\S]*?</search>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _extract_table(text: str) -> str:
    """Return from the first markdown table row onward."""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("|")), None)
    return "\n".join(lines[start:]).strip() if start is not None else ""


async def run(cfg: OrchestratorConfig, mcp_urls: list[str]) -> str:
    session_service = InMemorySessionService()
    runner = Runner(
        agent=_build_pipeline(cfg, mcp_urls),
        app_name="orchestrator",
        session_service=session_service,
    )
    session = await session_service.create_session(app_name="orchestrator", user_id="user")
    message = types.Content(role="user", parts=[types.Part(text=cfg.goal)])

    iteration = 0
    executor_table = ""

    ICONS = {"planner": "🧠 Planner", "executor": "⚙️  Executor", "critic": "🔍 Critic"}

    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
        author = getattr(event, "author", None)
        if not (event.content and event.content.parts):
            continue
        text = (event.content.parts[0].text or "").strip()
        if not text:
            continue

        if author == "planner":
            iteration += 1
            print(f"\n{'━'*50}", flush=True)
            print(f"  Iteration {iteration}", flush=True)
            print(f"{'━'*50}\n", flush=True)

        label = ICONS.get(author, author)

        if author == "planner":
            print(f"{label}\n{text}\n", flush=True)

        elif author == "executor":
            clean = _clean_executor(text)
            table = _extract_table(clean)
            if table:
                print(f"{label}  ✓ Produced result\n", flush=True)
                print(table, flush=True)
                print("", flush=True)
                if not executor_table:
                    executor_table = table
            else:
                print(f"{label}\n{clean[:300]}\n", flush=True)

        elif author == "critic":
            verdict = "✅ APPROVED" if "APPROVED" in text else "🔄 REVISE"
            summary = text[:300]
            print(f"{label}  →  {verdict}\n{summary}\n", flush=True)

    print(f"{'━'*50}", flush=True)
    print(f"  ✅ Complete — {iteration} iteration{'s' if iteration != 1 else ''}", flush=True)
    print(f"{'━'*50}\n", flush=True)

    return executor_table or "(no table produced)"
