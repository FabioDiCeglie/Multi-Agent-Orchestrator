from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

INSTRUCTION = """You are an execution agent. You receive a list of subtasks and execute them one by one using the tools available to you.

For each subtask:
1. Choose the most appropriate tool
2. Call it with the right arguments
3. Report the result clearly in markdown

Work through all subtasks in order. Be concise and factual.
"""


def create_executor(mcp_urls: list[str], model: str = "gemini-2.5-flash") -> LlmAgent:
    toolsets = [
        McpToolset(connection_params=StreamableHTTPConnectionParams(url=url))
        for url in mcp_urls
    ]
    return LlmAgent(
        name="executor",
        model=model,
        instruction=INSTRUCTION,
        tools=toolsets,
    )
