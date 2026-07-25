const AGENTS = [
  { icon: "🧠", label: "Planner" },
  { icon: "⚙️", label: "Executor" },
  { icon: "🔍", label: "Critic" },
];

interface AgentPipelineProps {
  /** Dims the pipeline into a subtle "working" treatment while a run is in flight. */
  loading?: boolean;
}

export function AgentPipeline({ loading = false }: AgentPipelineProps) {
  return (
    <div
      className={[
        "flex items-center gap-1.5 transition-opacity duration-300",
        loading ? "animate-pulse" : "",
      ].join(" ")}
    >
      {AGENTS.map((a, i) => (
        <span key={a.label} className="flex items-center gap-1.5">
          <span
            className={[
              "flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-medium transition-colors duration-300",
              loading
                ? "border-brand-500/40 bg-[rgba(99,102,241,0.08)] text-brand-400"
                : "border-border bg-surface-2 text-text-secondary",
            ].join(" ")}
          >
            {a.icon} {a.label}
          </span>

          {i < AGENTS.length - 1 && (
            <span className="text-text-muted text-xs leading-none">—</span>
          )}
        </span>
      ))}
    </div>
  );
}
