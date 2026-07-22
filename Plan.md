# Multi-Agent Orchestrator — Architecture Plan

> A reusable multi-agent system built on Google ADK and MCP tool use, with a simple polling-based UI.

---

## 1. System Overview

```mermaid
graph TD
    OP(("👤 Operator"))
    CLI["CLI\n--config goal.yaml\n--mcp-url ..."]
    ORCH["Orchestrator\nasyncio loop"]
    PL["🧠 Planner\nDecomposes goal"]
    EX["⚙️ Executor\nRuns subtasks"]
    CR["🔍 Critic\nEvaluates output"]
    MCP1["MCP Server A\ne.g. web_search"]
    MCP2["MCP Server B\ne.g. file_writer"]
    API["FastAPI\nREST API"]
    UI["Next.js Dashboard\nLoading → Results"]

    OP -->|"goal YAML"| CLI
    CLI --> ORCH
    ORCH --> PL
    PL -->|"subtasks"| EX
    EX -->|"results"| CR
    CR -->|"approved ✅\nor revision hints 🔄"| ORCH
    EX <-->|"tool calls"| MCP1
    EX <-->|"tool calls"| MCP2
    ORCH -->|"stores run log"| API
    UI -->|"GET /runs/{id}\nevery 2s"| API
```

---

## 2. Orchestration Loop

```mermaid
flowchart TD
    START([Pipeline Start]) --> PLAN
    PLAN["🧠 Planner\nBreaks goal into subtasks"]
    EXEC["⚙️ Executor\nRuns each subtask via MCP tools\nasync parallel where deps allow"]
    CRIT["🔍 Critic\nScores output against rubric"]
    APPROVE{Approved?\nor max iterations?}
    REVISE["Pack revision_hints\ninto context"]
    DONE([✅ Pipeline Complete\nStore final run log])

    START --> PLAN
    PLAN -->|"subtasks[]"| EXEC
    EXEC -->|"results[]"| CRIT
    CRIT --> APPROVE
    APPROVE -->|"Yes"| DONE
    APPROVE -->|"No"| REVISE
    REVISE -->|"iteration + 1"| PLAN
```

> Partial revision: the Critic can target individual failing subtasks, so the Planner only re-plans the minimum necessary set on each retry.

---

## 3. The Three Core Agents

```mermaid
graph LR
    subgraph PLANNER ["🧠 Planner"]
        PI["Input\ngoal + context\n(prev results + hints)"]
        PO["Output\nsubtasks[]\nreasoning"]
        PI --> PO
    end

    subgraph EXECUTOR ["⚙️ Executor"]
        EI["Input\nsubtask + mcp_tools[]"]
        EC["ADK agent\ncalls MCP tools"]
        EO["Output\nresult\ntool_calls[]"]
        EI --> EC --> EO
    end

    subgraph CRITIC ["🔍 Critic"]
        CI["Input\ngoal + results[]\nrubric + iteration"]
        CS["Score 0–1\nper rubric criterion"]
        CO["Output\napproved: bool\nfeedback\nrevision_hints[]"]
        CI --> CS --> CO
    end

    PO -->|"one subtask at a time"| EI
    EO -->|"all results"| CI
```

---

## 4. MCP Tool Injection

```mermaid
sequenceDiagram
    participant CLI
    participant Orch as Orchestrator Bootstrap
    participant MCP as MCP Server(s)
    participant ADK as ADK Executor Agent
    participant Handler as ToolCallHandler

    CLI->>Orch: --mcp-url http://localhost:8001/mcp
    Orch->>MCP: fetch tool manifest
    MCP-->>Orch: [{name, description, input_schema}]
    Orch->>ADK: inject as FunctionDeclaration[]
    Note over ADK: Executor sees only named tools,<br/>never raw MCP URLs

    ADK->>Handler: tool_call(name="web_search", args={...})
    Handler->>MCP: forward via MCP transport
    MCP-->>Handler: tool result
    Handler-->>ADK: result string
```

---

## 5. API & Polling (replaces streaming)

```mermaid
sequenceDiagram
    participant UI as Next.js UI
    participant API as FastAPI
    participant Orch as Orchestrator

    UI->>API: POST /runs {config}
    API-->>UI: {run_id, status: "running"}
    API->>Orch: start run (background task)

    loop every 2 seconds
        UI->>API: GET /runs/{run_id}
        API-->>UI: {status: "running", iteration: 2}
        Note over UI: Show spinner + current iteration
    end

    Orch-->>API: run complete → store full log
    UI->>API: GET /runs/{run_id}
    API-->>UI: {status: "complete", log: [...], result: "..."}
    Note over UI: Hide spinner, render results
```

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/runs` | Start a new run, returns `run_id` |
| `GET` | `/runs/{run_id}` | Poll status + current iteration |
| `GET` | `/runs/{run_id}/result` | Full run log + final result (once complete) |

### Run Status Model

```
RunStatus
├── run_id      UUID
├── status      "running" | "complete" | "error"
├── iteration   int  (current iteration number)
├── started_at  datetime
└── completed_at datetime | None

RunResult (returned when complete)
├── ...RunStatus fields
├── final_result   str
├── total_iterations int
├── critic_scores  list[float]   ← one per iteration
└── log            list[LogEntry]
    ├── iteration  int
    ├── subtasks   list[SubtaskResult]
    └── critic     CriticOutput
```

---

## 6. YAML Configuration Schema

```mermaid
graph TD
    CFG["goal.yaml"]
    CFG --> ORC["orchestrator\n─ goal: str\n─ max_iterations: int\n─ quality_threshold: float"]
    CFG --> MCP3["mcp_servers[]\n─ name: str\n─ url: AnyUrl"]
    CFG --> AGT["agents\n─ planner  {model, temperature}\n─ executor {model, temperature}\n─ critic   {model, temperature}"]
    CFG --> RUB["critic_rubric\n─ criteria[]\n  ─ name\n  ─ description\n  ─ weight  ← must sum to 1.0"]
```

---

## 7. Frontend Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Multi-Agent Orchestrator          Run: abc-123                 │
│  Goal: "Research top 5 LLM frameworks..."                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│               ⏳ Running...   Iteration 2 / 5                   │
│                                                                 │
│         🧠 Planner → ⚙️ Executor → 🔍 Critic  🔄              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  (empty while running — results appear here when complete)      │
└─────────────────────────────────────────────────────────────────┘

                         ↓  on complete

┌─────────────────────────────────────────────────────────────────┐
│  Multi-Agent Orchestrator          Run: abc-123   ✅ Approved   │
│  Goal: "Research top 5 LLM frameworks..."                       │
├─────────────────────────────────────────────────────────────────┤
│  Critic Score per Iteration   ▁▃▅▇█                            │
│  Completed in 3 iterations                                      │
├─────────────────────────────────────────────────────────────────┤
│  FINAL RESULT                                                   │
│  ─────────────────────────────────────────────────────────────  │
│  | Framework   | Stars | License | ... |                        │
│  | LangChain   | 90k   | MIT     | ... |                        │
│  | ...                                                          │
├─────────────────────────────────────────────────────────────────┤
│  RUN LOG  (collapsible per iteration)                           │
│  ▶ Iteration 1 — Score 0.62 — 4 subtasks                       │
│  ▶ Iteration 2 — Score 0.79 — 3 subtasks                       │
│  ▼ Iteration 3 — Score 0.91 — 2 subtasks  ✅                   │
│    Subtask 1: web_search → "..."                                │
│    Subtask 2: file_writer → saved comparison.md                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Folder Structure

```
multi-agent-orchestrator/
│
├── Plan.md
├── README.md
├── pyproject.toml                   ← uv / Python project
├── uv.lock
│
├── backend/
│   ├── agents/
│   │   ├── planner.py              ← PlannerAgent
│   │   ├── executor.py             ← ExecutorAgent
│   │   └── critic.py               ← CriticAgent
│   │
│   ├── orchestrator/
│   │   ├── loop.py                 ← async orchestration loop
│   │   ├── context.py              ← RunContext (shared state + log)
│   │   └── runner.py               ← top-level entrypoint
│   │
│   ├── mcp/
│   │   ├── client.py               ← connects to MCP servers
│   │   └── handler.py              ← ADK ToolCallHandler → MCP
│   │
│   ├── api/
│   │   ├── app.py                  ← FastAPI factory
│   │   ├── store.py                ← in-memory run store (dict of RunStatus)
│   │   └── routes/
│   │       └── runs.py             ← POST /runs, GET /runs/{id}, GET /runs/{id}/result
│   │
│   ├── config/
│   │   ├── schema.py               ← Pydantic Config + RunStatus models
│   │   └── loader.py               ← YAML → Config
│   │
│   ├── cli/
│   │   └── main.py                 ← Click CLI entry point
│   │
│   └── examples/
│       └── research_goal.yaml
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx            ← start a new run
│       │   └── run/[runId]/
│       │       └── page.tsx        ← dashboard (loading → results)
│       │
│       ├── components/
│       │   ├── RunningSpinner.tsx  ← spinner + iteration counter
│       │   ├── ResultView.tsx      ← final result display
│       │   ├── RunLog.tsx          ← collapsible iteration log
│       │   └── CriticScoreChart.tsx ← Recharts sparkline
│       │
│       ├── hooks/
│       │   └── useRunPoller.ts     ← polls GET /runs/{id} every 2s
│       │
│       └── types/
│           └── runs.ts             ← TypeScript mirror of RunStatus / RunResult
│
└── docker/
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── docker-compose.yml
```

---

## 9. Tech Stack

```mermaid
graph LR
    subgraph Backend ["Backend (Python 3.11+)"]
        ADK["Google ADK\nagent framework"]
        MCPS["MCP Python SDK\ntool transport"]
        FA2["FastAPI\nREST API"]
        PYD["Pydantic v2\nconfig + models"]
        CLK["Click\nCLI"]
        UV["uv\ndep management"]
    end

    subgraph Frontend ["Frontend (TypeScript)"]
        NX["Next.js 14\nApp Router"]
        TW["TailwindCSS\nstyling"]
        RC["Recharts\nscore sparkline"]
        PM["pnpm"]
    end

    FA2 <-->|"REST / polling"| NX
```

> Streaming removed: no WebSocket, no SSE, no Zustand, no event queue. Just `fetch` + a `useRunPoller` hook.

---

## 10. Build & Run — Local Dev

```mermaid
graph LR
    T1["Terminal 1\nuv run python -m backend.cli.main run\n--config examples/research_goal.yaml\n--mcp-url http://localhost:8001/mcp"]
    T2["Terminal 2\nMCP server\ne.g. web_search on :8001"]
    T3["Terminal 3\npnpm dev\nNext.js on :3000"]

    T2 <-->|"MCP transport"| T1
    T1 -->|"REST :8000"| T3
```

### Implementation Order

```mermaid
graph LR
    subgraph Phase1 ["Phase 1 — Backend"]
        direction TB
        C1["1. config/"] --> C2["2. mcp/"]
        C2 --> C3["3. agents/planner"]
        C3 --> C4["4. agents/executor"]
        C4 --> C5["5. agents/critic"]
        C5 --> C6["6. orchestrator/loop"]
        C6 --> C7["7. api/"]
        C7 --> C8["8. cli/"]
    end

    subgraph Phase2 ["Phase 2 — Frontend"]
        direction TB
        F1["1. types/runs.ts"] --> F2["2. hooks/useRunPoller"]
        F2 --> F3["3. RunningSpinner"]
        F3 --> F4["4. ResultView + RunLog"]
        F4 --> F5["5. CriticScoreChart"]
        F5 --> F6["6. Dashboard page"]
    end

    C8 --> F1
```

---

*Plan v1.2 — streaming replaced with polling.*
