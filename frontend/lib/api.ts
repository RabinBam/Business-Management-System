import type { ApiResponse, Task, WatcherStatus, Workflow, WorkflowCreate, Report, MarketingPlan } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.detail?.message ?? body?.error?.message ?? "The service could not complete the request.";
    throw new Error(message);
  }
  return (body as ApiResponse<T>).data;
}

export function createWorkflow(payload: WorkflowCreate) {
  return request<Workflow>("/workflows", { method: "POST", body: JSON.stringify(payload) });
}
export function getWorkflow(id: string) { return request<Workflow>(`/workflows/${id}`); }
export function runWorkflow(id: string) { return request<Workflow>(`/workflows/${id}/run`, { method: "POST" }); }
export function getTasks(id: string) { return request<Task[]>(`/workflows/${id}/tasks`); }
export function getWatcherStatus() { return request<WatcherStatus>("/watcher"); }
export function getReport(id: string) { return request<Report>(`/reports/${id}`); }
export function getMarketingPlan(id: string) { return request<MarketingPlan>(`/marketing/${id}`); }
export function updateMarketingPlan(id: string, plan: Partial<MarketingPlan>) { return request<MarketingPlan>(`/marketing/${id}`, { method: "PATCH", body: JSON.stringify(plan) }); }

