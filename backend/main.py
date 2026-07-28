from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import orchestrator
from config.schema import OrchestratorConfig
from models.context_file import ContextFile

app = FastAPI(title="Multi-Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_URLS = [u.strip() for u in os.getenv("MCP_URLS", "").split(",") if u.strip()]


class RunResult(BaseModel):
    result: str


@app.post("/runs", response_model=RunResult)
async def create_run(
    goal: str = Form(...),
    max_iterations: int = Form(5),
    files: list[UploadFile] = File(default=[]),
) -> RunResult:
    cfg = OrchestratorConfig(goal=goal, max_iterations=max_iterations)
    result = await orchestrator.run(cfg, MCP_URLS, await ContextFile.from_uploads(files))
    return RunResult(result=result)


@app.post("/runs/stream")
async def create_run_stream(
    goal: str = Form(...),
    max_iterations: int = Form(5),
    files: list[UploadFile] = File(default=[]),
) -> StreamingResponse:
    cfg = OrchestratorConfig(goal=goal, max_iterations=max_iterations)
    
    async def generate():
        async for event in orchestrator.run_stream(cfg, MCP_URLS, await ContextFile.from_uploads(files)):
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
