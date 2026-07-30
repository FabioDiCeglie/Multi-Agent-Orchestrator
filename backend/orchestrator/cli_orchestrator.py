from __future__ import annotations

import re

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

from orchestrator.base import BaseOrchestrator
from services.error_service import ErrorService


class CLIOrchestrator(BaseOrchestrator):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.console = Console()

    async def run(self) -> str:
        runner, session = await self._create_runner()
        message = self._build_message()

        try:
            async for event in runner.run_async(
                user_id="user", session_id=session.id, new_message=message,
            ):
                author = getattr(event, "author", None)
                if not (event.content and event.content.parts):
                    continue

                tool_calls = self.extract_tool_calls(event.content.parts)
                text = (event.content.parts[0].text or "").strip()
                if not text:
                    continue

                if author == "planner":
                    self._print_planner(text)
                elif author == "executor":
                    self._print_executor(text, tool_calls)
                elif author == "critic":
                    self._print_critic(text)
                elif author == "summarizer":
                    self._print_summarizer(text)
        except Exception as exc:
            self.console.print()
            self.console.print(Panel(
                ErrorService.clean_provider_error(exc),
                title="[bold red]❌ Error[/bold red]",
                border_style="red",
                padding=(1, 2),
            ))
            return ""

        self._print_complete()
        return self.summary_text or "(no result produced)"

    def _print_planner(self, text: str) -> None:
        self.iteration += 1
        self.console.print()
        self.console.print(Rule(
            f"[bold white] Iteration {self.iteration} [/bold white]",
            style="bright_blue",
        ))
        self.console.print()
        self.console.print(Panel(
            Markdown(text),
            title="[bold blue]🧠 Planner[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        ))

    def _print_executor(self, text: str, tool_calls: list[str]) -> None:
        clean = self.clean_executor(text)
        table_text = self._extract_table_text(clean)
        rich_table = self._parse_md_table(table_text) if table_text else None
        if tool_calls:
            label = ", ".join(tool_calls)
            title = f"[bold cyan]🔧 {label}[/bold cyan]"
        else:
            title = "[bold cyan]⚙️  Executor[/bold cyan]"
        self.console.print(Panel(
            rich_table if rich_table else Markdown(clean[:400]),
            title=title,
            border_style="cyan",
            padding=(1, 2),
        ))

    def _print_critic(self, text: str) -> None:
        approved = "APPROVED" in text
        color = "green" if approved else "yellow"
        icon = "✅" if approved else "🔄"
        verdict = "APPROVED" if approved else "REVISE"
        self.console.print(Panel(
            Markdown(text[:400]),
            title=(
                f"[bold {color}]🔍 Critic  →  "
                f"{icon} {verdict}[/bold {color}]"
            ),
            border_style=color,
            padding=(1, 2),
        ))

    def _print_summarizer(self, text: str) -> None:
        self.summary_text = text
        self.console.print(Panel(
            Markdown(text),
            title="[bold white]📝 Summarizer[/bold white]",
            border_style="white",
            padding=(1, 2),
        ))

    def _print_complete(self) -> None:
        self.console.print()
        self.console.print(Rule(
            f"[bold green] ✅ Complete — {self.iteration} "
            f"iteration{'s' if self.iteration != 1 else ''} [/bold green]",
            style="green",
        ))
        self.console.print()

    @staticmethod
    def _parse_md_table(text: str) -> Table | None:
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip().startswith("|")
        ]
        if len(lines) < 3:
            return None
        headers = [
            h.strip().strip("*") for h in lines[0].strip("|").split("|")
        ]
        table = Table(
            box=box.ROUNDED, header_style="bold cyan", show_lines=True,
        )
        for h in headers:
            table.add_column(h)
        for row_line in lines[2:]:
            cells = [c.strip() for c in row_line.strip("|").split("|")]
            cells = [re.sub(r"\*\*(.*?)\*\*", r"\1", c) for c in cells]
            if len(cells) == len(headers):
                table.add_row(*cells)
        return table

    @staticmethod
    def _extract_table_text(text: str) -> str:
        lines = text.split("\n")
        start = next(
            (i for i, line in enumerate(lines) if line.strip().startswith("|")),
            None,
        )
        return "\n".join(lines[start:]).strip() if start is not None else ""
