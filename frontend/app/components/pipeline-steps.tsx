import { AgentStep } from "@/app/components/agent-step";
import { PipelineStepEvent } from "@/app/lib/api";

export function PipelineSteps({ steps }: { steps: PipelineStepEvent[] }) {
  const iterations = new Map<number, PipelineStepEvent[]>();
  for (const step of steps) {
    iterations.set(step.iteration, [...(iterations.get(step.iteration) ?? []), step]);
  }

  return (
    <div className="flex flex-col gap-6">
      {Array.from(iterations.entries()).map(([iteration, iterationSteps]) => (
        <div key={iteration} className="flex flex-col gap-3">
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-medium uppercase tracking-widest text-text-muted">
              Iteration {iteration}
            </span>
            <div className="h-px flex-1 bg-border" />
          </div>
          <div className="flex flex-col gap-3">
            {iterationSteps.map((step, i) => (
              <AgentStep key={`${step.author}-${i}`} step={step} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
