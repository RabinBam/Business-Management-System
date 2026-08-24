import type {
  ApiResponse,
  MarketingPlan,
  Report,
  Task,
  WatcherStatus,
  Workflow,
  WorkflowCreate,
} from "./types";

const PUBLIC_API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

function getApiUrl(): string {
  if (typeof window === "undefined") {
    return process.env.INTERNAL_API_URL || PUBLIC_API_URL;
  }
  return PUBLIC_API_URL;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(
      body?.detail?.message ??
        body?.error?.message ??
        "The service could not complete the request.",
    );
  }
  return (body as ApiResponse<T>).data;
}

export function createWorkflow(payload: WorkflowCreate) {
  return request<Workflow>("/workflows", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}`);
}

export function runWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}/run`, { method: "POST" });
}

export function getTasks(id: string) {
  return request<Task[]>(`/workflows/${id}/tasks`);
}

export function getReport(id: string) {
  return request<Report>(`/workflows/${id}/report`);
}

export function getMarketingPlan(id: string) {
  return request<MarketingPlan>(`/workflows/${id}/marketing`);
}

export function updateMarketingPlan(id: string, plan: MarketingPlan) {
  return request<MarketingPlan>(`/workflows/${id}/marketing`, {
    method: "PUT",
    body: JSON.stringify(plan),
  });
}

export function getWatcherStatus() {
  return request<WatcherStatus>("/watcher");
}
