from __future__ import annotations

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import Tool

class MCPClient:
    @staticmethod
    def resolve_urls(csv: str) -> list[str]:
        """Split a comma-separated string of URLs into a clean list."""
        return [u.strip() for u in csv.split(",") if u.strip()]

    def __init__(self, name: str, url: str) -> None:
        self.name = name
        self.url = url
        self._session: ClientSession | None = None

    async def __aenter__(self) -> MCPClient:
        self._streams = await streamablehttp_client(self.url).__aenter__()
        read, write, _ = self._streams
        self._session = await ClientSession(read, write).__aenter__()
        await self._session.initialize()
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._session:
            await self._session.__aexit__(*args)

    async def list_tools(self) -> list[Tool]:
        assert self._session, "Client not connected — use async with MCPClient(...)"
        result = await self._session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, arguments: dict) -> str:
        assert self._session, "Client not connected — use async with MCPClient(...)"
        result = await self._session.call_tool(tool_name, arguments)
        return str(result.content[0].text) if result.content else ""
