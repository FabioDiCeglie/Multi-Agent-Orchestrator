"use client";

import { useState } from "react";

const AGENTS = [
  { icon: "🧠", label: "Planner" },
  { icon: "⚙️", label: "Executor" },
  { icon: "🔍", label: "Critic" },
];

const SUGGESTIONS = [
  "Top 5 LLM frameworks by GitHub stars",
  "Best open-source vector databases in 2025",
  "Compare Claude vs GPT vs Gemini for coding tasks",
];

export default function Home() {
  const [goal, setGoal] = useState("");

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && goal.trim()) {
      e.preventDefault();
      // will trigger submit once wired up
    }
  };

  return (
    <>
      <div className="orb" />

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-16">

        {/* Brand badge */}
        <div className="mb-10 flex items-center gap-2 rounded-full border border-[rgba(99,102,241,0.3)] bg-[rgba(99,102,241,0.08)] px-4 py-1.5 text-xs font-medium tracking-widest text-brand-400 uppercase">
          <span className="size-1.5 rounded-full bg-brand-400 animate-pulse" />
          Multi-Agent Orchestrator
        </div>

        {/* Heading */}
        <h1 className="mb-3 text-center text-4xl font-semibold tracking-tight text-text-primary">
          Give the pipeline a goal
        </h1>
        <p className="mb-10 text-center text-sm text-text-secondary max-w-sm">
          Three agents — Planner, Executor, Critic — will research,
          execute and verify until the answer is ready.
        </p>

        {/* Form card */}
        <div className="w-full max-w-xl rounded-2xl border border-border bg-surface-1 shadow-[0_0_80px_rgba(99,102,241,0.07)] overflow-hidden">

          {/* Textarea area — slightly lighter surface */}
          <div className="bg-surface-2 px-5 pt-5 pb-4">
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="e.g. Research the top 5 LLM frameworks by GitHub stars…"
              rows={4}
              className="w-full resize-none bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none leading-relaxed"
            />
            {/* Hint */}
            <p className="mt-1 text-[11px] text-text-muted text-right">
              {goal.length > 0 ? `${goal.length} chars · ` : ""}
              <kbd className="font-mono">⌘ Enter</kbd> to run
            </p>
          </div>

          {/* Bottom bar */}
          <div className="px-5 py-4 flex flex-col gap-4 bg-surface-1">

            {/* Agent pipeline pills */}
            <div className="flex items-center gap-1.5">
              {AGENTS.map((a, i) => (
                <span key={a.label} className="flex items-center gap-1.5">
                  <span className="flex items-center gap-1.5 rounded-full border border-border bg-surface-2 px-3 py-1 text-[11px] font-medium text-text-secondary">
                    {a.icon} {a.label}
                  </span>
                  {i < AGENTS.length - 1 && (
                    <span className="text-text-muted text-xs leading-none">—</span>
                  )}
                </span>
              ))}
            </div>

            {/* Run button */}
            <button
              disabled={!goal.trim()}
              className="w-full rounded-xl bg-brand-500 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 disabled:opacity-25 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-2"
            >
              Run pipeline
              <span className="text-base leading-none">→</span>
            </button>
          </div>
        </div>

        {/* Example suggestion chips */}
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

      </main>
    </>
  );
}
