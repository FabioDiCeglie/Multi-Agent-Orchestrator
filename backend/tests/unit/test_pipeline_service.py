from dataclasses import dataclass
from typing import Any

from services.pipeline_service import PipelineService


@dataclass
class FakeFunctionCall:
    name: str
    args: dict[str, Any]


@dataclass
class FakePart:
    function_call: FakeFunctionCall | None = None
    text: str | None = None


def test_clean_executor_strips_search_tags() -> None:
    raw = "Before <search>query</search> After"

    assert PipelineService.clean_executor(raw) == "Before  After"


def test_clean_executor_strips_html_tags() -> None:
    raw = "<div>Result</div>"

    assert PipelineService.clean_executor(raw) == "Result"


def test_extract_tool_calls_returns_names() -> None:
    parts = [
        FakePart(function_call=FakeFunctionCall("web_search", {"q": "test"})),
        FakePart(text="done"),
    ]

    assert PipelineService.extract_tool_calls(parts) == ["web_search"]


def test_extract_tool_calls_detailed_includes_args() -> None:
    parts = [
        FakePart(function_call=FakeFunctionCall("web_search", {"q": "test"})),
    ]

    assert PipelineService.extract_tool_calls_detailed(parts) == [
        {"name": "web_search", "args": {"q": "test"}},
    ]


def test_shape_planner_step() -> None:
    assert PipelineService.shape_planner_step(1, "1. Plan") == {
        "type": "step",
        "iteration": 1,
        "author": "planner",
        "text": "1. Plan",
    }


def test_shape_executor_step_with_tools() -> None:
    tool_calls = [{"name": "web_search", "args": {"q": "test"}}]
    mcp_urls = ["http://localhost:8001/mcp"]

    step = PipelineService.shape_executor_step(
        1, "<tag>Result</tag>", tool_calls, mcp_urls,
    )

    assert step == {
        "type": "step",
        "iteration": 1,
        "author": "executor",
        "text": "Result",
        "toolCalls": tool_calls,
        "mcpUrls": mcp_urls,
    }


def test_shape_executor_step_without_tools() -> None:
    step = PipelineService.shape_executor_step(1, "Result", [], [])

    assert step == {
        "type": "step",
        "iteration": 1,
        "author": "executor",
        "text": "Result",
    }
    assert "toolCalls" not in step
    assert "mcpUrls" not in step


def test_shape_critic_step_approved() -> None:
    assert PipelineService.shape_critic_step(1, "VERDICT: APPROVED") == {
        "type": "step",
        "iteration": 1,
        "author": "critic",
        "text": "VERDICT: APPROVED",
        "verdict": "APPROVED",
    }


def test_shape_critic_step_revise() -> None:
    step = PipelineService.shape_critic_step(2, "VERDICT: REVISE\n- fix table")

    assert step["verdict"] == "REVISE"
    assert step["iteration"] == 2


def test_shape_final_step() -> None:
    assert PipelineService.shape_final_step("Done", 2) == {
        "type": "final",
        "result": "Done",
        "iterations": 2,
    }
