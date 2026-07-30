from __future__ import annotations

import json
from typing import Any, AsyncIterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import main
from orchestrator.api_orchestrator import APIOrchestrator


async def _fake_run_stream(self) -> AsyncIterator[dict[str, Any]]:
    yield {"type": "step", "iteration": 1, "author": "planner", "text": "1. Do thing"}
    yield {"type": "final", "result": "Done", "iterations": 1}


async def _fake_error_run_stream(self) -> AsyncIterator[dict[str, Any]]:
    yield {"type": "error", "message": "Rate limit exceeded", "iteration": 1}


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


def test_health_returns_204(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 204
    assert response.content == b""


def test_root_serves_api_docs(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "swagger-ui" in response.text


@patch.object(APIOrchestrator, "run_stream", _fake_run_stream)
def test_runs_stream_returns_ndjson(client: TestClient) -> None:
    response = client.post(
        "/runs/stream",
        data={"goal": "Research LLM frameworks", "max_iterations": "2"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/x-ndjson")

    events = [json.loads(line) for line in response.text.strip().split("\n") if line]
    assert events[0]["type"] == "step"
    assert events[0]["author"] == "planner"
    assert events[-1] == {"type": "final", "result": "Done", "iterations": 1}


@patch.object(APIOrchestrator, "run_stream", _fake_error_run_stream)
def test_runs_stream_returns_error_event(client: TestClient) -> None:
    response = client.post(
        "/runs/stream",
        data={"goal": "Test", "max_iterations": "2"},
    )

    assert response.status_code == 200
    events = [json.loads(line) for line in response.text.strip().split("\n") if line]
    assert events == [{"type": "error", "message": "Rate limit exceeded", "iteration": 1}]


@patch.object(APIOrchestrator, "run_stream", _fake_run_stream)
def test_runs_stream_passes_mcp_urls(client: TestClient) -> None:
    created: list[APIOrchestrator] = []
    original_init = APIOrchestrator.__init__

    def capture_init(self, cfg, urls, files=None) -> None:
        created.append(self)
        original_init(self, cfg, urls, files)

    with patch.object(APIOrchestrator, "__init__", capture_init):
        response = client.post(
            "/runs/stream",
            data={
                "goal": "Test",
                "mcp_urls": "http://localhost:8001/mcp, http://localhost:8002/mcp",
            },
        )

    assert response.status_code == 200
    assert len(created) == 1
    assert created[0].mcp_urls == [
        "http://localhost:8001/mcp",
        "http://localhost:8002/mcp",
    ]


def test_runs_stream_rejects_too_many_files(client: TestClient) -> None:
    files = [("files", (f"file{i}.txt", b"data", "text/plain")) for i in range(11)]

    response = client.post("/runs/stream", data={"goal": "Test"}, files=files)

    assert response.status_code == 400
    assert "Too many files" in response.json()["detail"]


def test_runs_stream_rejects_oversized_file(client: TestClient) -> None:
    with patch.object(main, "MAX_FILE_SIZE", 10):
        response = client.post(
            "/runs/stream",
            data={"goal": "Test"},
            files=[("files", ("big.txt", b"x" * 20, "text/plain"))],
        )

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"]
