"use client";

import { AgentStep } from "@/app/components/agent-step";
import { CopyButton } from "@/app/components/copy-button";
import { ErrorPanel } from "@/app/components/error-panel";
import { PipelineSteps } from "@/app/components/pipeline-steps";
import { AsyncStatus, useAsync } from "@/app/hooks/use-async";
import { PipelineStepEvent, RunPipelineParams, runPipelineStream } from "@/app/lib/api";
import { useCallback, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const SUGGESTIONS = [
  "Top 5 LLM frameworks by GitHub stars",
  "Best open-source vector databases in 2025",
  "Compare Claude vs GPT vs Gemini for coding tasks",
];

export default function Home() {
  const [goal, setGoal] = useState("");
  const [steps, setSteps] = useState<PipelineStepEvent[]>([]);

  const streamPipeline = useCallback(
    async ({ goal, maxIterations }: RunPipelineParams, signal: AbortSignal) => {
      let result = "";
      await runPipelineStream(
        { goal, maxIterations },
        (event) => {
          if (event.type === "step") setSteps((prev) => [...prev, event]);
          else result = event.result;
        },
        signal
      );
      return result;
    },
    []
  );

  const { status, data: result, error, run, cancel, reset } = useAsync(streamPipeline);

  const handleRun = () => {
    if (!goal.trim()) return;
    setSteps([]);
    run({ goal, maxIterations: 3 });
  };

  const handleReset = () => {
    setSteps([]);
    reset();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleRun();
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-4 py-16">

      {/* ── IDLE ── */}
      {status === AsyncStatus.IDLE && (
        <>
          <div className="mb-10 flex items-center gap-2 rounded-full border border-border bg-surface-1 px-4 py-1.5 text-xs font-medium tracking-widest text-brand-500 uppercase">
            <span className="size-1.5 rounded-full bg-brand-500" />
            Multi-Agent Orchestrator
          </div>

          <h1 className="mb-3 text-center text-4xl font-semibold tracking-tight text-text-primary">
            Give the pipeline a goal
          </h1>
          <p className="mb-10 text-center text-sm text-text-secondary max-w-sm">
            Three agents — Planner, Executor, Critic — will research,
            execute and verify until the answer is ready.
          </p>

          <div className="w-full max-w-xl rounded-2xl border border-border bg-surface-1 shadow-sm overflow-hidden">
            <div className="border-b border-transparent px-5 pt-5 pb-4 transition-colors focus-within:border-b-border">
              <textarea
                autoFocus
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g. Research the top 5 LLM frameworks by GitHub stars…"
                rows={4}
                className="w-full resize-none bg-transparent text-sm text-text-primary placeholder-text-muted focus:outline-none leading-relaxed"
              />
              <p className="mt-1 text-[11px] text-text-muted text-right">
                {goal.length > 0 ? `${goal.length} chars · ` : ""}
                <kbd className="rounded border border-border bg-surface-2 px-1 py-0.5 font-mono">⌘ Enter</kbd> to run
              </p>
            </div>

            <div className="px-5 py-4 flex flex-col gap-4 bg-surface-1">
              <button
                onClick={handleRun}
                disabled={!goal.trim()}
                className="w-full rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-700 disabled:opacity-30 disabled:cursor-not-allowed active:scale-[0.98] flex items-center justify-center gap-2"
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

      {status === AsyncStatus.LOADING && (
        <div className="w-full max-w-4xl flex flex-col gap-6">
          <div className="flex flex-col items-center gap-3 text-center">
            <p className="text-xs font-medium tracking-widest text-text-muted uppercase">Running</p>
            <p className="text-lg font-medium text-text-primary max-w-md">&quot;{goal}&quot;</p>
            <div className="flex items-center gap-2 text-xs text-text-muted">
              <span className="size-3 rounded-full border border-border-hover border-t-brand-500 animate-spin" />
              {steps.length === 0 ? "Starting up…" : "Working through the pipeline…"}
            </div>
            <button
              onClick={cancel}
              className="mt-1 rounded-full border border-border px-3 py-1.5 text-xs text-text-secondary transition-colors hover:border-border-hover hover:text-text-primary focus-visible:outline-2 focus-visible:outline-brand-500/50"
            >
              Cancel
            </button>
          </div>

          {steps.length > 0 && (
            <div className="result-scroll max-h-[65vh] overflow-y-auto pr-2">
              <AgentStep step={steps[steps.length - 1]} collapsible={false} />
            </div>
          )}
        </div>
      )}

      {status === AsyncStatus.SUCCESS && (
        <div className="w-full max-w-4xl flex flex-col gap-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-emerald-400 text-sm">✓</span>
              <span className="text-sm font-medium text-text-primary">Complete</span>
            </div>
            <button
              onClick={handleReset}
              className="-mr-2.5 rounded-full px-2.5 py-1 text-xs text-text-secondary transition-colors hover:bg-surface-2 hover:text-text-primary focus-visible:outline-2 focus-visible:outline-brand-500/50"
            >
              ← Run again
            </button>
          </div>

          <div className="rounded-2xl border border-border bg-surface-1 p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <p className="text-xs text-text-secondary font-medium uppercase tracking-widest">Result</p>
              <CopyButton text={result ?? ""} />
            </div>
            <div className="result-scroll max-h-[60vh] overflow-y-auto overflow-x-auto pr-2">
              <div className="prose prose-app max-w-none text-sm text-text-primary leading-relaxed">
                <Markdown remarkPlugins={[remarkGfm]}>{result}</Markdown>
              </div>
            </div>
          </div>

          {steps.length > 0 && (
            <details className="rounded-2xl border border-border bg-surface-1 p-6 shadow-sm">
              <summary className="cursor-pointer text-xs text-text-muted font-medium uppercase tracking-widest">
                Pipeline steps ({steps.length})
              </summary>
              <div className="mt-4">
                <PipelineSteps steps={steps} />
              </div>
            </details>
          )}
        </div>
      )}

      {status === AsyncStatus.ERROR && <ErrorPanel message={error} onRetry={handleReset} />}

    </main>
  );
}
