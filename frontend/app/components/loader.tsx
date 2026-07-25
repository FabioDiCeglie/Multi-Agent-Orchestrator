import { AgentPipeline } from "@/app/components/agent-pipeline";

interface LoaderProps {
  goal: string;
}

export function Loader({ goal }: LoaderProps) {
  return (
    <div className="flex flex-col items-center gap-8 text-center">
      <div className="flex flex-col items-center gap-3">
        <p className="text-xs font-medium tracking-widest text-text-muted uppercase">Running</p>
        <p className="text-lg font-medium text-text-primary max-w-md">&quot;{goal}&quot;</p>
      </div>
      <AgentPipeline loading />
      <div className="flex items-center gap-2 text-xs text-text-muted">
        <span className="size-3 rounded-full border border-text-muted border-t-transparent animate-spin" />
        This may take a minute…
      </div>
    </div>
  );
}
