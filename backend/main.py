from __future__ import annotations

import json
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.schema import OrchestratorConfig
from mcp_client.client import MCPClient
from models.context_file import ContextFile
from orchestrator import APIOrchestrator

app = FastAPI(title="Multi-Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/runs/stream")
async def create_run_stream(
    goal: str = Form(...),
    max_iterations: int = Form(5),
    mcp_urls: str | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
) -> StreamingResponse:
    cfg = OrchestratorConfig(goal=goal, max_iterations=max_iterations)
    urls = MCPClient.resolve_urls(mcp_urls or "")

    async def generate():
        context = await ContextFile.from_uploads(files)
        orch = APIOrchestrator(cfg, urls, context)
        async for event in orch.run_stream():
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
