from services.mcp_service import McpService


def test_parse_urls_splits_and_trims() -> None:
    assert McpService.parse_urls(
        " http://localhost:8001/mcp , http://localhost:8002/mcp "
    ) == [
        "http://localhost:8001/mcp",
        "http://localhost:8002/mcp",
    ]


def test_parse_urls_ignores_empty_segments() -> None:
    assert McpService.parse_urls("http://a/mcp,, ,http://b/mcp") == [
        "http://a/mcp",
        "http://b/mcp",
    ]


def test_parse_urls_empty_string() -> None:
    assert McpService.parse_urls("") == []


def test_parse_urls_single_url() -> None:
    assert McpService.parse_urls("http://localhost:8001/mcp") == [
        "http://localhost:8001/mcp",
    ]
