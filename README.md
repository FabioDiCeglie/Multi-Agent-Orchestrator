# Multi-Agent Orchestrator

A goal-driven AI pipeline built on [Google ADK](https://google.github.io/adk-docs/) and [MCP](https://modelcontextprotocol.io/) tool use. Four agents — Planner, Executor, Critic, Summarizer — loop until the answer is ready.

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
| Frontend | `cd frontend && npm install && npm run dev` | :3000  |
| CLI      | `uv run orchestrator run --config examples/research_goal.yaml` | —  |

Requires `ANTHROPIC_API_KEY` in `backend/.env` for Claude access via LiteLLM.

### Tests

```bash
cd backend && uv sync --group dev && uv run pytest -v
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
    model: "claude-sonnet-4-6"
```

`agent` is optional — defaults to `claude-sonnet-4-6` if omitted.

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
