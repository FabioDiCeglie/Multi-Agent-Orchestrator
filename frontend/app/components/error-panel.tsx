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
          className="-mr-2.5 rounded-full px-2.5 py-1 text-xs text-text-secondary transition-colors hover:bg-surface-2 hover:text-text-primary focus-visible:outline-2 focus-visible:outline-brand-500/50"
        >
          ← Try again
        </button>
      </div>

      <div className="rounded-2xl border border-red-500/20 bg-red-500/10 p-6">
        <p className="text-xs text-red-400 mb-3 font-medium uppercase tracking-widest">Error</p>
        <p className="text-sm text-text-primary leading-relaxed">{message}</p>
      </div>
    </div>
  );
}
