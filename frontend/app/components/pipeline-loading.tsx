import { AgentStep } from "@/app/components/agent-step";
import { PipelineStepEvent } from "@/app/lib/api";

interface PipelineLoadingProps {
  goal: string;
  steps: PipelineStepEvent[];
  onCancel: () => void;
}

export function PipelineLoading({ goal, steps, onCancel }: PipelineLoadingProps) {
  return (
    <div className="w-full max-w-4xl flex flex-col gap-6">
      <div className="flex flex-col items-center gap-3 text-center">
        <p className="text-xs font-medium tracking-widest text-text-muted uppercase">Running</p>
        <p className="text-lg font-medium text-text-primary max-w-md">&quot;{goal}&quot;</p>
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <span className="size-3 rounded-full border border-border-hover border-t-brand-500 animate-spin" />
          {steps.length === 0 ? "Starting up…" : "Working through the pipeline…"}
        </div>
        <button
          onClick={onCancel}
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
  );
}
