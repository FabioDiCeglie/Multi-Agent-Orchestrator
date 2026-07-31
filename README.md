# Multi-Agent Orchestrator

A goal-driven AI pipeline built on [Google ADK](https://google.github.io/adk-docs/) and [MCP](https://modelcontextprotocol.io/) tool use. Four agents — Planner, Executor, Critic, Summarizer — loop until the answer is ready.

**Live demo:** [multi-agent-orchestrator-ten.vercel.app](https://multi-agent-orchestrator-ten.vercel.app/)

See [DOCS.md](./DOCS.md) for architecture and design decisions.

## Architecture

```
User  →  CLI / FastAPI  →  Orchestrator
                                │
                          LoopAgent (max N)
                           ┌─────────────┐
                           │  Planner    │ break goal into subtasks
                           │  Executor   │ run subtasks via MCP tools
                           │  Critic     │ APPROVED → exit / REVISE → loop
                           └─────────────┘
                                │
                          SummarizerAgent
                                │
                           Final result
```

## Local running

Copy `.env.example` to `.env` inside `backend/`, then:

```bash
cd backend && uv sync
```

| Service  | Command                                  | Port   |
| -------- | ---------------------------------------- | ------ |
| Backend  | `uv run uvicorn main:app --reload`       | :8000  |
| API docs | —                                        | http://localhost:8000/ |
| Frontend | `cd frontend && npm install && npm run dev` | :3000  |
| CLI      | `uv run orchestrator run --config examples/research_goal.yaml` | —  |

Requires `GEMINI_API_KEY` in `backend/.env` for Gemini access via LiteLLM (default model: `gemini/gemini-3-flash-preview`).

### Docker Compose

One command for backend + frontend with hot reload (runs in the background):

```bash
cp backend/.env.example backend/.env   # add your GEMINI_API_KEY
docker compose up --build -d
```

Useful commands:

```bash
docker compose logs -f          # follow logs
docker compose ps               # container status
docker compose down             # stop
docker compose down -v          # stop and remove volumes (fresh start)
```

| Service  | URL                   |
| -------- | --------------------- |
| Frontend | http://localhost:3000 |
| Backend  | http://localhost:8000 |
| API docs | http://localhost:8000/ |

If MCP servers run on your host machine (not in Docker), use `http://host.docker.internal:PORT/mcp` instead of `localhost` in the UI — the backend container can't reach `localhost` on your host.

### Tests

```bash
cd backend && uv sync --group dev

# All tests
uv run pytest -v

# Unit only
uv run pytest tests/unit -v

# Integration only
uv run pytest tests/integration -v
```

### MCP servers (optional)

Connect external tools by passing MCP server URLs at runtime:

```bash
# CLI
uv run orchestrator run --config examples/research_goal.yaml --mcp-url http://localhost:8001/mcp

# API / Frontend
# Add URLs via the MCP Servers section in the UI, or pass mcp_urls in the form data
```

### Context files

Attach files for the executor to reference:

```bash
# CLI
uv run orchestrator run --config examples/research_goal.yaml --file notes.md --file data.csv

# API / Frontend
# Upload via the file attachment UI or multipart form
```

## YAML config

```yaml
orchestrator:
  goal: "Research the top 5 LLM frameworks and produce a comparison table."
  max_iterations: 3
  agent:
    model: "gemini/gemini-3-flash-preview"
```

`agent` is optional — defaults to `gemini/gemini-3-flash-preview` if omitted.

## Project layout

```
backend/
  main.py                 # FastAPI — POST /runs/stream (NDJSON)
  cli.py                  # Click CLI entry point
  agents/
    planner.py            # PlannerAgent — breaks goal into subtasks
    executor.py           # ExecutorAgent — runs subtasks via MCP tools
    critic.py             # CriticAgent — approves or requests revision
    summarizer.py         # SummarizerAgent — polished final answer
  orchestrator/
    base.py               # Shared pipeline builder (ADK LoopAgent + SequentialAgent)
    cli_orchestrator.py   # CLI event consumer (Rich terminal output)
    api_orchestrator.py   # API event consumer (NDJSON stream)
  config/
    schema.py             # OrchestratorConfig, AgentConfig (Pydantic)
    loader.py             # YAML config loader
  models/
    context_file.py       # ContextFile dataclass (file uploads)
  examples/
    research_goal.yaml    # Sample goal config
    dj_instagram.yaml     # Sample goal config
    sample-context.md     # Sample context file

frontend/
  app/
    page.tsx              # Main UI (goal input → streaming → result)
    lib/api.ts            # Backend streaming client
    hooks/use-async.ts    # Generic async state machine
    components/           # UI components (pipeline steps, error panel, etc.)
```

## Tech stack

**Backend:** Python 3.11+, Google ADK, LiteLLM, FastAPI, Pydantic, Click, Rich, uv

**Frontend:** Next.js 16, React 19, Tailwind CSS 4, react-markdown
