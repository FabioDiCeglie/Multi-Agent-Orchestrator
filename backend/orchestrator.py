from __future__ import annotations

import re

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

    iteration = 0
    executor_table_text = ""

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
            if rich_table:
                console.print(Panel(
                    rich_table,
                    title="[bold cyan]⚙️  Executor[/bold cyan]",
                    border_style="cyan",
                    padding=(1, 2),
                ))
                if not executor_table_text:
                    executor_table_text = table_text
            else:
                console.print(Panel(
                    Markdown(clean[:400]),
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

    console.print()
    console.print(Rule(
        f"[bold green] ✅ Complete — {iteration} iteration{'s' if iteration != 1 else ''} [/bold green]",
        style="green",
    ))
    console.print()

    return executor_table_text or "(no table produced)"
