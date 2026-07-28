import { PipelineStepEvent } from "@/app/lib/api";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AGENT_META = {
  planner: { icon: "🧠", label: "Planner", border: "border-blue-500/30", text: "text-blue-400" },
  executor: { icon: "⚙️", label: "Executor", border: "border-cyan-500/30", text: "text-cyan-400" },
  critic: { icon: "🔍", label: "Critic", border: "border-amber-500/30", text: "text-amber-400" },
  summarizer: { icon: "📝", label: "Summarizer", border: "border-text-muted/30", text: "text-text-secondary" },
} as const;

interface AgentStepProps {
  step: PipelineStepEvent;
  /** When false, renders as an always-open panel (used for the live "currently running" step) instead of a dropdown. */
  collapsible?: boolean;
}

export function AgentStep({ step, collapsible = true }: AgentStepProps) {
  const meta = AGENT_META[step.author];
  const isApproved = step.verdict === "APPROVED";
  const border = step.author === "critic" ? (isApproved ? "border-emerald-500/30" : "border-amber-500/30") : meta.border;
  const text = step.author === "critic" ? (isApproved ? "text-emerald-400" : meta.text) : meta.text;

  const header = (
    <div className={`flex items-center justify-between px-4 py-3 ${collapsible ? "" : "border-b border-border"}`}>
      <span className={`flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest ${text}`}>
        {meta.icon} {meta.label}
      </span>
      <div className="flex items-center gap-2">
        {step.verdict && (
          <span className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${
            isApproved
              ? "border-emerald-500/30 text-emerald-400"
              : "border-amber-500/30 text-amber-400"
          }`}>
            {isApproved ? "✅ APPROVED" : "🔄 REVISE"}
          </span>
        )}
        {collapsible && (
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="shrink-0 text-text-muted transition-transform duration-150 group-open:rotate-90"
          >
            <path d="M9 18l6-6-6-6" />
          </svg>
        )}
      </div>
    </div>
  );

  const body = (
    <div className={`result-scroll overflow-x-auto px-4 py-3 ${collapsible ? "border-t border-border" : ""}`}>
      <div className="prose prose-app prose-sm max-w-none text-text-primary leading-relaxed">
        <Markdown remarkPlugins={[remarkGfm]}>{step.text}</Markdown>
      </div>
    </div>
  );

  if (!collapsible) {
    return (
      <div className={`rounded-xl border ${border} bg-surface-1 overflow-hidden`}>
        {header}
        {body}
      </div>
    );
  }

  return (
    <details className={`group rounded-xl border ${border} bg-surface-1 overflow-hidden`}>
      <summary className="cursor-pointer list-none [&::-webkit-details-marker]:hidden">{header}</summary>
      {body}
    </details>
  );
}
