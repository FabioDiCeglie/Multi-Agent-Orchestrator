from __future__ import annotations


class McpService:
    @staticmethod
    def parse_urls(csv: str) -> list[str]:
        """Split a comma-separated string of MCP URLs into a clean list."""
        return [url.strip() for url in csv.split(",") if url.strip()]
