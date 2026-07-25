interface ErrorPanelProps {
  message?: string;
  onRetry: () => void;
}

export function ErrorPanel({ message, onRetry }: ErrorPanelProps) {
  return (
    <div className="w-full max-w-xl flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-red-400 text-sm">✕</span>
          <span className="text-sm font-medium text-text-primary">Something went wrong</span>
        </div>
        <button
          onClick={onRetry}
          className="text-xs text-text-muted hover:text-text-secondary transition-colors"
        >
          ← Try again
        </button>
      </div>

      <div className="rounded-2xl border border-red-500/20 bg-[rgba(239,68,68,0.06)] p-6">
        <p className="text-xs text-red-400/80 mb-3 font-medium uppercase tracking-widest">Error</p>
        <p className="text-sm text-text-primary leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
