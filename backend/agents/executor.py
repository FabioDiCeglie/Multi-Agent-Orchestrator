from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

from config.schema import DEFAULT_MODEL
from models.context_file import ContextFile

INSTRUCTION = """You are an execution agent. You receive a list of subtasks and execute them one by one using the tools available to you.

For each subtask:
1. Choose the most appropriate tool
2. Call it with the right arguments
3. Report the result clearly in markdown

Work through all subtasks in order. Be concise and factual.

If context files are available, use read_context_file to read them before starting your work.
"""


def _build_file_reader(files: list[ContextFile]):
    """Build a closure over the provided files so the LLM can read them by name."""
    lookup = {f.name: f.content for f in files}

    def read_context_file(filename: str) -> str:
        """Read the content of an attached context file by its name."""
        if filename in lookup:
            return lookup[filename]
        available = ", ".join(lookup.keys()) or "none"
        return f"File '{filename}' not found. Available: {available}"

    return read_context_file


class ExecutorAgent(LlmAgent):
    def __init__(
        self,
        mcp_urls: list[str],
        context_files: list[ContextFile] | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        tools: list = [
            McpToolset(
                connection_params=StreamableHTTPConnectionParams(url=url),
            )
            for url in mcp_urls
        ]
        if context_files:
            tools.append(_build_file_reader(context_files))
        super().__init__(
            name="executor",
            model=LiteLlm(model=model),
            instruction=INSTRUCTION,
            tools=tools,
        )
