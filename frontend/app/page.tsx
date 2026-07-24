"use client";

import { useState } from "react";

const AGENTS = [
  { icon: "🧠", label: "Planner" },
  { icon: "⚙️", label: "Executor" },
  { icon: "🔍", label: "Critic" },
];

export default function Home() {
  const [goal, setGoal] = useState("");

  return (
    <>
      {/* Background orb */}
      <div className="orb" />

      <main className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-16">
        {/* Brand badge */}
        <div className="mb-10 flex items-center gap-2 rounded-full border border-[rgba(99,102,241,0.3)] bg-[rgba(99,102,241,0.08)] px-4 py-1.5 text-xs font-medium tracking-widest text-brand-400 uppercase">
          <span className="size-1.5 rounded-full bg-brand-400 animate-pulse" />
          Orchestrator
        </div>

        {/* Heading */}
        <h1 className="mb-3 text-center text-4xl font-semibold tracking-tight text-text-primary">
          What do you want to research?
        </h1>
        <p className="mb-10 text-center text-sm text-text-secondary">
          Describe a goal — the agent pipeline will plan, execute and verify it for you.
        </p>

        {/* Form card */}
        <div className="w-full max-w-xl rounded-2xl border border-border bg-surface-1 p-5 shadow-[0_0_60px_rgba(99,102,241,0.06)]">
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="e.g. Research the top 5 LLM frameworks by GitHub stars…"
            rows={4}
            className="w-full resize-none bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none leading-relaxed"
          />

          {/* Divider */}
          <div className="my-4 h-px bg-[rgba(255,255,255,0.06)]" />

          {/* Agent pipeline */}
          <div className="flex items-center gap-2 mb-4">
            {AGENTS.map((a, i) => (
              <span key={a.label} className="flex items-center gap-1.5">
                <span className="text-xs text-text-secondary">
                  {a.icon} {a.label}
                </span>
                {i < AGENTS.length - 1 && (
                  <span className="text-text-muted text-xs">→</span>
                )}
              </span>
            ))}
          </div>

          {/* Run button */}
          <button
            disabled={!goal.trim()}
            className="w-full rounded-xl bg-brand-500 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-600 disabled:opacity-30 disabled:cursor-not-allowed active:scale-[0.98]"
          >
            Run
          </button>
        </div>
      </main>
    </>
  );
}
