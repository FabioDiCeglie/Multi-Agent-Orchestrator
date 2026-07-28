import { PipelineStepEvent } from "@/app/lib/api";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

const AGENT_META = {
  planner: { icon: "🧠", label: "Planner", border: "border-blue-500/30", text: "text-blue-400" },
  executor: { icon: "⚙️", label: "Executor", border: "border-cyan-500/30", text: "text-cyan-400" },
  critic: { icon: "🔍", label: "Critic", border: "border-amber-500/30", text: "text-amber-400" },
} as const;

export function AgentStep({ step }: { step: PipelineStepEvent }) {
  const meta = AGENT_META[step.author];
  const isApproved = step.verdict === "APPROVED";
  const border = step.author === "critic" ? (isApproved ? "border-green-500/30" : "border-amber-500/30") : meta.border;
  const text = step.author === "critic" ? (isApproved ? "text-green-400" : meta.text) : meta.text;

  return (
    <details className={`group rounded-xl border ${border} bg-surface-2 overflow-hidden`}>
      <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-3 [&::-webkit-details-marker]:hidden">
        <span className={`flex items-center gap-1.5 text-xs font-semibold uppercase tracking-widest ${text}`}>
          {meta.icon} {meta.label}
        </span>
        <div className="flex items-center gap-2">
          {step.verdict && (
            <span className={`rounded-full border px-2 py-0.5 text-[11px] font-medium ${
              isApproved
                ? "border-green-500/30 text-green-400"
                : "border-amber-500/30 text-amber-400"
            }`}>
              {isApproved ? "✅ APPROVED" : "🔄 REVISE"}
            </span>
          )}
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
        </div>
      </summary>
      <div className="result-scroll overflow-x-auto border-t border-border px-4 py-3">
        <div className="prose prose-invert prose-sm max-w-none text-text-primary leading-relaxed">
          <Markdown remarkPlugins={[remarkGfm]}>{step.text}</Markdown>
        </div>
      </div>
    </details>
  );
}
