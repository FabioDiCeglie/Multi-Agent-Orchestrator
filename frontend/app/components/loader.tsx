const AGENTS = [
  { icon: "🧠", label: "Planner" },
  { icon: "⚙️", label: "Executor" },
  { icon: "🔍", label: "Critic" },
];

interface LoaderProps {
  goal: string;
}

/** Shown while a run is in flight — echoes the goal and animates the pipeline. */
export function Loader({ goal }: LoaderProps) {
  return (
    <div className="flex flex-col items-center gap-8 text-center">
      <div className="flex flex-col items-center gap-3">
        <p className="text-xs font-medium tracking-widest text-text-muted uppercase">Running</p>
        <p className="text-lg font-medium text-text-primary max-w-md">&quot;{goal}&quot;</p>
      </div>

      <div className="flex items-center gap-1.5 animate-pulse">
        {AGENTS.map((a, i) => (
          <span key={a.label} className="flex items-center gap-1.5">
            <span className="flex items-center gap-1.5 rounded-full border border-brand-500/40 bg-[rgba(99,102,241,0.08)] px-3 py-1 text-[11px] font-medium text-brand-400">
              {a.icon} {a.label}
            </span>

            {i < AGENTS.length - 1 && (
              <span className="text-text-muted text-xs leading-none">—</span>
            )}
          </span>
        ))}
      </div>

      <div className="flex items-center gap-2 text-xs text-text-muted">
        <span className="size-3 rounded-full border border-text-muted border-t-transparent animate-spin" />
        This may take a minute…
      </div>
    </div>
  );
}
