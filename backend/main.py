from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import orchestrator
from config.schema import OrchestratorConfig

app = FastAPI(title="Multi-Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_URLS = [u.strip() for u in os.getenv("MCP_URLS", "").split(",") if u.strip()]


class RunRequest(BaseModel):
    goal: str
    max_iterations: int = 5


class RunResult(BaseModel):
    result: str


@app.post("/runs", response_model=RunResult)
async def create_run(req: RunRequest) -> RunResult:
    cfg = OrchestratorConfig(goal=req.goal, max_iterations=req.max_iterations)
    result = await orchestrator.run(cfg, MCP_URLS)
    return RunResult(result=result)


@app.post("/runs/stream")
async def create_run_stream(req: RunRequest) -> StreamingResponse:
    cfg = OrchestratorConfig(goal=req.goal, max_iterations=req.max_iterations)

    async def generate():
        async for event in orchestrator.run_stream(cfg, MCP_URLS):
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
