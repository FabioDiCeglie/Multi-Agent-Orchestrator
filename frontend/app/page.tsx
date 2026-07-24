"use client";

import { useState } from "react";
import { AgentPipeline } from "@/app/components/agent-pipeline";

type State = "idle" | "loading" | "done" | "error";

const SUGGESTIONS = [
  "Top 5 LLM frameworks by GitHub stars",
  "Best open-source vector databases in 2025",
  "Compare Claude vs GPT vs Gemini for coding tasks",
];

// Cycles through agent indices 0→1→2 while loading
function useAgentCycle(active: boolean) {
  const [index, setIndex] = useState(0);

  useState(() => {
    if (!active) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % 3), 2200);
    return () => clearInterval(id);
  });

  return active ? index : undefined;
}

export default function Home() {
  const [goal, setGoal] = useState("");
  const [state, setState] = useState<State>("idle");
  const [result, setResult] = useState("");
  const activeAgent = useAgentCycle(state === "loading");

  const handleRun = async () => {
    if (!goal.trim()) return;
    setState("loading");
    setResult("");

    try {
      const res = await fetch("http://localhost:8000/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal, max_iterations: 3 }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data.result);
      setState("done");
    } catch (err) {
      console.error(err);
      setState("error");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleRun();
    }
  };

  const reset = () => {
    setState("idle");
    setResult("");
  };

  return (
    <>
      <div className="orb" />

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-16">

        {/* ── IDLE ── */}
        {state === "idle" && (
          <>
            <div className="mb-10 flex items-center gap-2 rounded-full border border-[rgba(99,102,241,0.3)] bg-[rgba(99,102,241,0.08)] px-4 py-1.5 text-xs font-medium tracking-widest text-brand-400 uppercase">
              <span className="size-1.5 rounded-full bg-brand-400 animate-pulse" />
              Multi-Agent Orchestrator
            </div>

            <h1 className="mb-3 text-center text-4xl font-semibold tracking-tight text-text-primary">
              Give the pipeline a goal
            </h1>
            <p className="mb-10 text-center text-sm text-text-secondary max-w-sm">
              Three agents — Planner, Executor, Critic — will research,
              execute and verify until the answer is ready.
            </p>

            <div className="w-full max-w-xl rounded-2xl border border-border bg-surface-1 shadow-[0_0_80px_rgba(99,102,241,0.07)] overflow-hidden">
              <div className="bg-surface-2 px-5 pt-5 pb-4">
                <textarea
                  value={goal}
                  onChange={(e) => setGoal(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g. Research the top 5 LLM frameworks by GitHub stars…"
                  rows={4}
                  className="w-full resize-none bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none leading-relaxed"
                />
                <p className="mt-1 text-[11px] text-text-muted text-right">
                  {goal.length > 0 ? `${goal.length} chars · ` : ""}
                  <kbd className="font-mono">⌘ Enter</kbd> to run
                </p>
              </div>

              <div className="px-5 py-4 flex flex-col gap-4 bg-surface-1">
                <AgentPipeline />
                <button
                  onClick={handleRun}
                  disabled={!goal.trim()}
                  className="w-full rounded-xl bg-brand-500 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 disabled:opacity-25 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-2"
                >
                  Run pipeline →
                </button>
              </div>
            </div>

            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => setGoal(s)}
                  className="rounded-full border border-border bg-surface-1 px-3 py-1.5 text-xs text-text-secondary transition-colors hover:border-border-hover hover:text-text-primary"
                >
                  {s}
                </button>
              ))}
            </div>
          </>
        )}

        {/* ── LOADING ── */}
        {state === "loading" && (
          <div className="flex flex-col items-center gap-8 text-center">
            <div className="flex flex-col items-center gap-3">
              <p className="text-xs font-medium tracking-widest text-text-muted uppercase">Running</p>
              <p className="text-lg font-medium text-text-primary max-w-md">"{goal}"</p>
            </div>
            <AgentPipeline activeIndex={activeAgent} />
            <p className="text-xs text-text-muted animate-pulse">This may take a minute…</p>
          </div>
        )}

        {/* ── DONE ── */}
        {state === "done" && (
          <div className="w-full max-w-2xl flex flex-col gap-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-green-400 text-sm">✓</span>
                <span className="text-sm font-medium text-text-primary">Complete</span>
              </div>
              <button
                onClick={reset}
                className="text-xs text-text-muted hover:text-text-secondary transition-colors"
              >
                ← Run again
              </button>
            </div>

            <div className="rounded-2xl border border-border bg-surface-1 p-6">
              <p className="text-xs text-text-muted mb-4 font-medium uppercase tracking-widest">Result</p>
              <pre className="text-sm text-text-primary whitespace-pre-wrap font-mono leading-relaxed">
                {result}
              </pre>
            </div>

            <AgentPipeline />
          </div>
        )}

        {/* ── ERROR ── */}
        {state === "error" && (
          <div className="flex flex-col items-center gap-4 text-center">
            <p className="text-sm text-red-400">Something went wrong. Is the backend running?</p>
            <button
              onClick={reset}
              className="text-xs text-text-muted hover:text-text-secondary transition-colors"
            >
              ← Try again
            </button>
          </div>
        )}

      </main>
    </>
  );
}
