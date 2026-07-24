const AGENTS = [
  { icon: "🧠", label: "Planner" },
  { icon: "⚙️", label: "Executor" },
  { icon: "🔍", label: "Critic" },
];

interface AgentPipelineProps {
  activeIndex?: number;
}

export function AgentPipeline({ activeIndex }: AgentPipelineProps) {
  return (
    <div className="flex items-center gap-1.5">
      {AGENTS.map((a, i) => {
        const isActive = i === activeIndex;
        const isDone = activeIndex !== undefined && i < activeIndex;

        return (
          <span key={a.label} className="flex items-center gap-1.5">
            <span
              className={[
                "flex items-center gap-1.5 rounded-full border px-3 py-1 text-[11px] font-medium transition-all duration-300",
                isActive
                  ? "border-brand-500 bg-[rgba(99,102,241,0.12)] text-brand-400 shadow-[0_0_12px_rgba(99,102,241,0.25)]"
                  : isDone
                  ? "border-border bg-surface-2 text-text-secondary opacity-50"
                  : "border-border bg-surface-2 text-text-secondary",
              ].join(" ")}
            >
              {/* Spinner replaces icon when active */}
              {isActive ? (
                <span className="size-3 rounded-full border border-brand-400 border-t-transparent animate-spin" />
              ) : (
                a.icon
              )}
              {a.label}
            </span>

            {i < AGENTS.length - 1 && (
              <span
                className={[
                  "text-xs leading-none transition-colors duration-300",
                  isDone ? "text-text-secondary" : "text-text-muted",
                ].join(" ")}
              >
                —
              </span>
            )}
          </span>
        );
      })}
    </div>
  );
}
