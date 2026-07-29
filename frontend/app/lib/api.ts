const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface RunPipelineParams {
  goal: string;
  maxIterations?: number;
  files?: File[];
  mcpUrls?: string[];
}

export type AgentAuthor = "planner" | "executor" | "critic" | "summarizer";

export interface PipelineStepEvent {
  type: "step";
  iteration: number;
  author: AgentAuthor;
  text: string;
  verdict?: "APPROVED" | "REVISE";
}

export interface PipelineFinalEvent {
  type: "final";
  result: string;
  iterations: number;
}

export type PipelineEvent = PipelineStepEvent | PipelineFinalEvent;

/**
 * Streams each Planner/Executor/Critic step as it happens (newline-delimited JSON),
 * invoking `onEvent` per step/final event. Resolves once the stream ends.
 */
export async function runPipelineStream(
  { goal, maxIterations = 3, files = [], mcpUrls = [] }: RunPipelineParams,
  onEvent: (event: PipelineEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const body = new FormData();
  body.set("goal", goal);
  body.set("max_iterations", String(maxIterations));
  if (mcpUrls.length > 0) body.set("mcp_urls", mcpUrls.join(","));
  for (const file of files) body.append("files", file);

  const res = await fetch(`${API_BASE}/runs/stream`, {
    method: "POST",
    body,
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Request failed (HTTP ${res.status}). Is the backend running?`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      onEvent(JSON.parse(line) as PipelineEvent);
    }
  }

  if (buffer.trim()) {
    onEvent(JSON.parse(buffer) as PipelineEvent);
  }
}
