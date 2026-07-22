import asyncio

import click

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
    click.echo("Orchestrator starting... (agents not wired yet)")
