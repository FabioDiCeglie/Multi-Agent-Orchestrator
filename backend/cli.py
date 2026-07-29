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
from rich.panel import Panel
from rich.markdown import Markdown

load_dotenv()

import orchestrator
from config.loader import ConfigLoader
from mcp_client.client import MCPClient
from models.context_file import ContextFile


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--config", required=True, type=click.Path(exists=True), help="Path to goal YAML file")
@click.option("--mcp-url", multiple=True, help="MCP server URL (can be repeated)")
@click.option("--file", "files", multiple=True, type=click.Path(exists=True), help="Context file (can be repeated)")
def run(config: str, mcp_url: tuple[str, ...], files: tuple[str, ...]) -> None:
    cfg = ConfigLoader(config).load()
    env_urls = MCPClient.resolve_urls(os.getenv("MCP_URLS", ""))
    urls = env_urls + list(mcp_url)

    click.echo(f"Goal: {cfg.goal}")
    click.echo(f"Max iterations: {cfg.max_iterations}")
    click.echo(f"MCP servers: {urls or 'none'}")
    click.echo(f"Context files: {list(files) or 'none'}")

    context_files = [ContextFile(name=os.path.basename(path), content=open(path).read()) for path in files]
    result = asyncio.run(orchestrator.run(cfg, urls, context_files))
    Console().print(Panel(
        Markdown(result),
        title="[bold white]📋 Final Result[/bold white]",
        border_style="white",
        padding=(1, 2),
    ))


if __name__ == "__main__":
    cli()
