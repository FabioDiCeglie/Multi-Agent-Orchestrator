from __future__ import annotations

import re
from typing import Any, AsyncIterator

from google.adk.agents import LoopAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from agents.critic import CriticAgent
from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.summarizer import SummarizerAgent
from config.schema import OrchestratorConfig

console = Console()


def _parse_md_table(text: str) -> Table | None:
    """Parse a markdown table string into a Rich Table."""
    lines = [l.strip() for l in text.split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return None
    headers = [h.strip().strip("*") for h in lines[0].strip("|").split("|")]
    table = Table(box=box.ROUNDED, header_style="bold cyan", show_lines=True)
    for h in headers:
        table.add_column(h)
    for row_line in lines[2:]:
        cells = [c.strip() for c in row_line.strip("|").split("|")]
        cells = [re.sub(r"\*\*(.*?)\*\*", r"\1", c) for c in cells]
        if len(cells) == len(headers):
            table.add_row(*cells)
    return table


def _clean_executor(text: str) -> str:
    text = re.sub(r"<search[\s\S]*?</search>", "", text, flags=re.IGNORECASE)
    return re.sub(r"<[^>]+>", "", text).strip()


def _extract_table_text(text: str) -> str:
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip().startswith("|")), None)
    return "\n".join(lines[start:]).strip() if start is not None else ""


def _build_pipeline(cfg: OrchestratorConfig, mcp_urls: list[str]) -> SequentialAgent:
    return SequentialAgent(
        name="orchestrator",
        sub_agents=[
            LoopAgent(
                name="planning_loop",
                max_iterations=cfg.max_iterations,
                sub_agents=[
                    SequentialAgent(
                        name="pipeline",
                        sub_agents=[PlannerAgent(), ExecutorAgent(mcp_urls), CriticAgent()],
                    )
                ],
            ),
            SummarizerAgent(),
        ],
    )


def _build_prompt(goal: str, files: list[str]) -> str:
    if not files:
        return goal
    parts = ["## Context Files\n"]
    for path in files:
        with open(path) as f:
            content = f.read()
        parts.append(f"### {path}\n```\n{content}\n```\n")
    parts.append(f"## Goal\n{goal}")
    return "\n".join(parts)


async def run(cfg: OrchestratorConfig, mcp_urls: list[str], files: list[str] | None = None) -> str:
    session_service = InMemorySessionService()
    runner = Runner(
        agent=_build_pipeline(cfg, mcp_urls),
        app_name="orchestrator",
        session_service=session_service,
    )
    session = await session_service.create_session(app_name="orchestrator", user_id="user")
    prompt = _build_prompt(cfg.goal, files or [])
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    iteration = 0
    summary_text = ""

    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
        author = getattr(event, "author", None)
        if not (event.content and event.content.parts):
            continue
        text = (event.content.parts[0].text or "").strip()
        if not text:
            continue

        if author == "planner":
            iteration += 1
            console.print()
            console.print(Rule(f"[bold white] Iteration {iteration} [/bold white]", style="bright_blue"))
            console.print()
            console.print(Panel(
                Markdown(text),
                title="[bold blue]🧠 Planner[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            ))

        elif author == "executor":
            clean = _clean_executor(text)
            table_text = _extract_table_text(clean)
            rich_table = _parse_md_table(table_text) if table_text else None
            console.print(Panel(
                rich_table if rich_table else Markdown(clean[:400]),
                title="[bold cyan]⚙️  Executor[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            ))

        elif author == "critic":
            approved = "APPROVED" in text
            color = "green" if approved else "yellow"
            icon = "✅" if approved else "🔄"
            verdict = "APPROVED" if approved else "REVISE"
            console.print(Panel(
                Markdown(text[:400]),
                title=f"[bold {color}]🔍 Critic  →  {icon} {verdict}[/bold {color}]",
                border_style=color,
                padding=(1, 2),
            ))

        elif author == "summarizer":
            summary_text = text
            console.print(Panel(
                Markdown(text),
                title="[bold white]📝 Summarizer[/bold white]",
                border_style="white",
                padding=(1, 2),
            ))

    console.print()
    console.print(Rule(
        f"[bold green] ✅ Complete — {iteration} iteration{'s' if iteration != 1 else ''} [/bold green]",
        style="green",
    ))
    console.print()

    return summary_text or "(no result produced)"


async def run_stream(
    cfg: OrchestratorConfig, mcp_urls: list[str], files: list[str] | None = None
) -> AsyncIterator[dict[str, Any]]:
    """API entry point — yields one dict per Planner/Executor/Critic step, then a final event.

    Separate from `run()` (used by the CLI) so the CLI's `rich` console output is
    never affected by changes made here for the web UI.
    """
    session_service = InMemorySessionService()
    runner = Runner(
        agent=_build_pipeline(cfg, mcp_urls),
        app_name="orchestrator",
        session_service=session_service,
    )
    session = await session_service.create_session(app_name="orchestrator", user_id="user")
    prompt = _build_prompt(cfg.goal, files or [])
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    iteration = 0
    summary_text = ""

    async for event in runner.run_async(user_id="user", session_id=session.id, new_message=message):
        author = getattr(event, "author", None)
        if not (event.content and event.content.parts):
            continue
        text = (event.content.parts[0].text or "").strip()
        if not text:
            continue

        if author == "planner":
            iteration += 1
            yield {"type": "step", "iteration": iteration, "author": "planner", "text": text}

        elif author == "executor":
            clean = _clean_executor(text)
            yield {"type": "step", "iteration": iteration, "author": "executor", "text": clean}

        elif author == "critic":
            verdict = "APPROVED" if "APPROVED" in text else "REVISE"
            yield {
                "type": "step", "iteration": iteration, "author": "critic",
                "text": text, "verdict": verdict,
            }

        elif author == "summarizer":
            summary_text = text
            yield {"type": "step", "iteration": iteration, "author": "summarizer", "text": text}

    yield {
        "type": "final", "result": summary_text or "(no result produced)", "iterations": iteration,
    }
