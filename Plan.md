# Multi-Agent Orchestrator — Architecture Plan

> A reusable multi-agent system built on Google ADK and MCP tool use, with a simple loading UI.

---

## 1. System Overview

```mermaid
graph TD
    OP(("👤 Operator"))
    CLI["cli.py\n--config goal.yaml\n--mcp-url ..."]
    ORCH["orchestrator.py\nLoopAgent + SequentialAgent"]
    PL["🧠 PlannerAgent"]
    EX["⚙️ ExecutorAgent"]
    CR["🔍 CriticAgent"]
    MCP["MCP Server(s)\nvia MCP_URLS env var"]
    API["main.py\nFastAPI — POST /runs"]
    UI["Next.js\nSpinner → Result"]

    OP -->|"goal YAML"| CLI
    OP -->|"POST {goal}"| API
    CLI --> ORCH
    API --> ORCH
    ORCH --> PL
    PL --> EX
    EX --> CR
    CR -->|"VERDICT: APPROVED\nescalate=True"| ORCH
    EX <-->|"McpToolset"| MCP
    ORCH -->|"result"| API
    API -->|"RunResult"| UI
```

---

## 2. Orchestration Loop (ADK-native)

```mermaid
flowchart TD
    START([POST /runs — goal received]) --> LOOP

    subgraph LOOP ["LoopAgent (max_iterations)"]
        direction TB
        PL["🧠 PlannerAgent\nnumbered markdown subtasks"]
        EX["⚙️ ExecutorAgent\nruns subtasks via MCP tools"]
        CR["🔍 CriticAgent\nVERDICT: APPROVED or REVISE"]
        PL --> EX --> CR
    end

    CR -->|"APPROVED\nescalate=True"| DONE
    CR -->|"REVISE\nnext iteration"| PL
    DONE([✅ Return final result])
```

> ADK handles iteration and context passing automatically — no manual loop code.

---

## 3. The Three Agents

```mermaid
graph LR
    subgraph PA ["🧠 PlannerAgent(LlmAgent)"]
        P1["Sees: goal + full conversation history"]
        P2["Outputs: numbered markdown subtask list"]
        P1 --> P2
    end

    subgraph EA ["⚙️ ExecutorAgent(LlmAgent)"]
        E1["Sees: subtasks from Planner"]
        E2["McpToolset injects tools from MCP_URLS"]
        E3["Outputs: markdown results per subtask"]
        E1 --> E2 --> E3
    end

    subgraph CA ["🔍 CriticAgent(LlmAgent)"]
        C1["Sees: full conversation"]
        C2["Outputs: feedback + VERDICT"]
        C3["after_agent_callback\nchecks for APPROVED\nsets escalate=True"]
        C1 --> C2 --> C3
    end

    P2 --> E1
    E3 --> C1
```

---

## 4. MCP Tool Injection

```mermaid
sequenceDiagram
    participant Env as MCP_URLS env var
    participant Exec as ExecutorAgent
    participant ADK as McpToolset (ADK)
    participant MCP as MCP Server

    Env->>Exec: list of MCP URLs at startup
    Exec->>ADK: McpToolset(StreamableHTTPConnectionParams)
    ADK->>MCP: fetch tool manifest
    MCP-->>ADK: [{name, description, schema}]
    Note over Exec: Gemini sees tool names + descriptions<br/>and decides which to call

    Exec->>ADK: tool_call("web_search", {...})
    ADK->>MCP: forward call
    MCP-->>ADK: result
    ADK-->>Exec: result string
```

---

## 5. API — Single Endpoint

```mermaid
sequenceDiagram
    participant UI as Next.js
    participant API as FastAPI (main.py)
    participant Orch as orchestrator.run()

    UI->>API: POST /runs {goal, max_iterations}
    API->>Orch: await orchestrator.run(cfg, MCP_URLS)
    Note over API,Orch: Blocks until pipeline completes
    Orch-->>API: final result string
    API-->>UI: {result: "..."}
    Note over UI: Hide spinner, render result
```

### Models

```
RunRequest   → goal: str, max_iterations: int
RunResult    → result: str
```

---

## 6. YAML Config

```mermaid
graph TD
    CFG["examples/research_goal.yaml"]
    CFG --> G["goal: str"]
    CFG --> M["max_iterations: int"]
```

> Minimal on purpose — MCP URLs come from the `MCP_URLS` env var, not the config file.

---

## 7. Frontend Layout

```
┌──────────────────────────────────────────┐
│  Multi-Agent Orchestrator                │
│  Goal: "Research top 5 LLM frameworks"   │
├──────────────────────────────────────────┤
│                                          │
│    ⏳ Running...                         │
│    🧠 → ⚙️ → 🔍  (animated)             │
│                                          │
└──────────────────────────────────────────┘

              ↓  when POST /runs returns

┌──────────────────────────────────────────┐
│  ✅ Complete                             │
├──────────────────────────────────────────┤
│  RESULT                                  │
│  ──────────────────────────────────────  │
│  | Framework  | Stars | License | ...  │ │
│  | LangChain  | 90k   | MIT     | ...  │ │
└──────────────────────────────────────────┘
```

---

## 8. Actual Folder Structure

```
multi-agent-orchestrator/
│
├── Plan.md
├── README.md
├── .gitignore
│
└── backend/
    ├── pyproject.toml              ← uv project + dependencies
    ├── uv.lock
    ├── .venv/
    │
    ├── main.py                     ← FastAPI, POST /runs
    ├── orchestrator.py             ← functional pipeline (LoopAgent)
    ├── cli.py                      ← Click CLI entry point
    │
    ├── agents/
    │   ├── planner.py              ← PlannerAgent(LlmAgent)
    │   ├── executor.py             ← ExecutorAgent(LlmAgent) + McpToolset
    │   └── critic.py               ← CriticAgent(LlmAgent) + escalate callback
    │
    ├── config/
    │   ├── schema.py               ← OrchestratorConfig, AgentConfig
    │   └── loader.py               ← ConfigLoader class
    │
    ├── mcp/
    │   └── client.py               ← MCPClient (direct use / testing)
    │
    └── examples/
        └── research_goal.yaml
```

> Frontend not built yet — coming in Phase 2.

---

## 9. Tech Stack

```mermaid
graph LR
    subgraph Backend ["Backend (Python 3.11+)"]
        ADK["Google ADK 2.5\nLoopAgent, SequentialAgent\nLlmAgent, McpToolset"]
        FA["FastAPI + uvicorn\nPOST /runs"]
        PYD["Pydantic v2\nconfig + API models"]
        CLK["Click\nCLI"]
        UV["uv\ndep management"]
    end

    subgraph Frontend ["Frontend — Phase 2"]
        NX["Next.js 14"]
        TW["TailwindCSS"]
    end

    FA <-->|"HTTP"| NX
```

---

## 10. Local Dev

```mermaid
graph LR
    T1["Terminal 1\nMCP server on :8001\nexport MCP_URLS=http://localhost:8001/mcp"]
    T2["Terminal 2\ncd backend\nuv run uvicorn main:app --reload"]
    T3["Terminal 3\ncd backend\nuv run python cli.py run\n--config examples/research_goal.yaml"]

    T1 <-->|"MCP"| T2
    T1 <-->|"MCP"| T3
```

---

*Plan v1.3 — reflects actual implementation.*
