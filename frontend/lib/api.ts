import type {
  ApiResponse,
  Dashboard,
  ManagementReview,
  MarketingPlan,
  Report,
  Task,
  WatcherStatus,
  Worker,
  WorkerResult,
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
    credentials: "include",
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

export function listWorkflows() {
  return request<Workflow[]>("/workflows");
}

export function runWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}/run`, { method: "POST" });
}

export function refineWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}/refine`, { method: "POST" });
}

export function retryWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}/retry`, { method: "POST" });
}

export function cancelWorkflow(id: string) {
  return request<Workflow>(`/workflows/${id}/cancel`, { method: "POST" });
}

export function getTasks(id: string) {
  return request<Task[]>(`/workflows/${id}/tasks`);
}

export function getWorkerResults(id: string) {
  return request<WorkerResult[]>(`/workflows/${id}/results`);
}

export function getManagementReviews(id: string) {
  return request<ManagementReview[]>(`/workflows/${id}/reviews`);
}

export function getWorkers() {
  return request<Worker[]>("/workers");
}

export function getDashboard() {
  return request<Dashboard>("/dashboard");
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
