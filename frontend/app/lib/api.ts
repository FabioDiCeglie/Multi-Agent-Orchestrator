const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface RunPipelineParams {
  goal: string;
  maxIterations?: number;
}

export async function runPipeline({
  goal,
  maxIterations = 3,
}: RunPipelineParams): Promise<string> {
  const res = await fetch(`${API_BASE}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, max_iterations: maxIterations }),
  });

  if (!res.ok) {
    throw new Error(`Request failed (HTTP ${res.status}). Is the backend running?`);
  }

  const data = await res.json();
  return data.result as string;
}
