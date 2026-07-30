const PRESETS = [1, 2, 3, 5] as const;

interface MaxIterationsProps {
  value: number;
  onChange: (value: number) => void;
}

export function MaxIterations({ value, onChange }: MaxIterationsProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="text-[11px] text-text-muted">Iterations</span>
      <div className="flex items-center gap-1" role="group" aria-label="Max iterations">
        {PRESETS.map((n) => {
          const active = value === n;
          return (
            <button
              key={n}
              type="button"
              onClick={() => onChange(n)}
              aria-pressed={active}
              className={`min-w-7 rounded-md px-2 py-1 text-[11px] tabular-nums transition-colors ${
                active
                  ? "bg-surface-3 text-text-primary"
                  : "text-text-muted hover:bg-surface-2 hover:text-text-secondary"
              }`}
            >
              {n}
            </button>
          );
        })}
      </div>
    </div>
  );
}
