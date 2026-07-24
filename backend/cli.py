import asyncio
import os
import warnings

# Disable OpenTelemetry — ADK's tracing throws context errors on generator cancellation
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
# Suppress ADK experimental feature warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.adk")

import click
from dotenv import load_dotenv

load_dotenv()

from config.loader import ConfigLoader


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to goal YAML file")
@click.option("--mcp-url", multiple=True, help="MCP server URL (can be repeated)")
def run(config: str, mcp_url: tuple[str, ...]) -> None:
    cfg = ConfigLoader(config).load()
    click.echo(f"Goal: {cfg.goal}")
    click.echo(f"Max iterations: {cfg.max_iterations}")
    click.echo(f"MCP servers: {list(mcp_url) or 'none'}")
    asyncio.run(_run(cfg, list(mcp_url)))


async def _run(cfg, mcp_urls: list[str]) -> None:
    import orchestrator
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    console = Console()
    result = await orchestrator.run(cfg, mcp_urls)
    console.print(Panel(
        Markdown(result),
        title="[bold white]📋 Final Result[/bold white]",
        border_style="white",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    cli()
