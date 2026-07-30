import asyncio
import os
import warnings

# Disable OpenTelemetry — ADK's tracing throws context errors on generator cancellation
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
# Suppress ADK and Google auth warnings
warnings.filterwarnings("ignore", category=UserWarning)

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

load_dotenv()

from config.loader import ConfigLoader
from models.context_file import ContextFile
from orchestrator import CLIOrchestrator


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "--config", required=True, type=click.Path(exists=True),
    help="Path to goal YAML file",
)
@click.option("--mcp-url", multiple=True, help="MCP server URL (repeatable)")
@click.option(
    "--file", "files", multiple=True, type=click.Path(exists=True),
    help="Context file (repeatable)",
)
def run(config: str, mcp_url: tuple[str, ...], files: tuple[str, ...]) -> None:
    console = Console()
    cfg = ConfigLoader(config).load()
    env_csv = os.getenv("MCP_URLS", "")
    env_urls = [u.strip() for u in env_csv.split(",") if u.strip()]
    urls = env_urls + list(mcp_url)

    context_files = []
    for p in files:
        with open(p, encoding="utf-8") as f:
            context_files.append(ContextFile(name=os.path.basename(p), content=f.read()))

    info = Table.grid(padding=(0, 2))
    info.add_column(style="bold")
    info.add_column()
    info.add_row("Goal", cfg.goal)
    info.add_row("Iterations", str(cfg.max_iterations))
    servers = ", ".join(urls) if urls else "[dim]none[/dim]"
    info.add_row("MCP servers", servers)
    if context_files:
        for i, f in enumerate(context_files):
            label = "Files" if i == 0 else ""
            size = f"{len(f.content):,} chars"
            info.add_row(label, f"📎 {f.name} [dim]({size})[/dim]")
    else:
        info.add_row("Files", "[dim]none[/dim]")
    console.print(Panel(
        info,
        title="[bold white]⚡ Pipeline Config[/bold white]",
        border_style="bright_blue",
        padding=(1, 2),
    ))
    console.print()

    orch = CLIOrchestrator(cfg, urls, context_files)
    result = asyncio.run(orch.run())
    console.print(Panel(
        Markdown(result),
        title="[bold white]📋 Final Result[/bold white]",
        border_style="white",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    cli()
