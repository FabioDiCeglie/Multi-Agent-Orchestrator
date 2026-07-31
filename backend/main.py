from __future__ import annotations

import json
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile

load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config.schema import OrchestratorConfig
from models.context_file import ContextFile
from orchestrator import APIOrchestrator
from services.mcp_service import McpService

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB per file
MAX_FILES = 10

CORS_ORIGINS = [
    o.strip().rstrip("/")
    for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if o.strip()
]

app = FastAPI(title="Multi-Agent Orchestrator", docs_url="/", redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=204)
async def health() -> None:
    return


@app.post("/runs/stream")
async def create_run_stream(
    goal: str = Form(...),
    max_iterations: int = Form(2),
    mcp_urls: str | None = Form(default=None),
    files: list[UploadFile] = File(default=[]),
) -> StreamingResponse:
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Too many files (max {MAX_FILES})")
    for f in files:
        size = len(await f.read())
        await f.seek(0)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File '{f.filename}' exceeds {MAX_FILE_SIZE // (1024 * 1024)} MB limit",
            )

    cfg = OrchestratorConfig(goal=goal, max_iterations=max_iterations)
    urls = McpService.parse_urls(mcp_urls or "")

    async def generate():
        context = await ContextFile.from_uploads(files)
        orch = APIOrchestrator(cfg, urls, context)
        async for event in orch.run_stream():
            yield json.dumps(event) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
