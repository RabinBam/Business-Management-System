export type WorkflowStatus =
  | "CREATED" | "SEGMENTING" | "ASSIGNING" | "EXECUTING" | "REVIEWING"
  | "REPORTING" | "MARKETING" | "FINAL_REVIEW" | "COMPLETED" | "FAILED"
  | "CANCELLED";

export type TaskStatus = "PENDING" | "RUNNING" | "SUBMITTED" | "COMPLETED" | "FAILED";

export interface WorkflowCreate { title: string; objective: string; budget: number; deadline: string; execution_mode?: "ai" | "employee"; sales_history?: number[]; }
export interface ExecutiveSummary {
  objective: string;
  overview: string;
  major_work_completed: string[];
  financial_summary: string;
  sales_prediction: string;
  marketing_strategy: string;
  major_risks: string[];
  management_recommendation: string;
}
export interface WorkflowFailure { code: string; message: string; failed_stage: WorkflowStatus; }
export interface Workflow extends WorkflowCreate {
  id: string;
  status: WorkflowStatus;
  current_stage: string;
  created_at: string;
  updated_at?: string;
  started_at?: string | null;
  completed_at?: string | null;
  failure?: WorkflowFailure | null;
  executive_summary?: ExecutiveSummary | null;
}

export interface Task {
  id: string;
  workflow_id: string;
  title: string;
  description: string;
  priority: string;
  difficulty: number;
  required_role: string;
  minimum_experience_years: number;
  required_skills: string[];
  dependency_task_ids: string[];
  expected_output: string;
  acceptance_criteria: string[];
  employee_brief?: string;
  handoff_notes?: string;
  status: TaskStatus;
  estimated_cost?: number;
  assigned_worker_id?: string | null;
  assigned_worker_name?: string | null;
  assignment_reason?: string | null;
  revision_count?: number;
  revision_instructions?: string[];
}

export interface Worker {
  id: string;
  name: string;
  role: string;
  experience_years: number;
  skills: string[];
  department: string;
  availability: "AVAILABLE" | "BUSY" | string;
  workload_percent: number;
  active_tasks: number;
}

export interface WorkerResult {
  task_id: string;
  worker_id: string;
  summary: string;
  output: Record<string, unknown>;
  evidence: string[];
  cost: number;
  assignment_reason: string;
}

export interface ManagementReview {
  task_id: string;
  decision: "APPROVED" | "REVISION_REQUIRED";
  feedback: string;
  acceptance_criteria_met: string[];
  revision_instructions: string[];
}

export interface FinancialSummary { total_budget: number; planned_spend: number; remaining_budget: number; }
export interface SalesPrediction { current_sales: number; predicted_sales: number; growth_percent: number; method: string; }
export interface Report { workflow_id: string; financial: FinancialSummary; sales_prediction: SalesPrediction; risks: string[]; recommendations: string[]; }
export interface BudgetAllocation { channel: string; amount: number; reason: string; }
export interface MarketingPlan { workflow_id: string; approved_budget: number; objective: string; target_audience: string; allocations: BudgetAllocation[]; timeline: string[]; expected_outcome: string; }

export type WatcherState = "IDLE" | "ACTIVE";
export interface WatcherEvent { workflow_id: string | null; component: string; event_type: string; message: string; retry_count: number; resolved: boolean; created_at: string; }
export interface WatcherStatus { state: WatcherState; active_incidents: number; events: WatcherEvent[]; }
export interface DashboardMetrics {
  workflow_count: number;
  active_workflows: number;
  completed_workflows: number;
  failed_workflows: number;
  total_budget: number;
  planned_spend: number;
  available_budget: number;
  predicted_growth_percent: number;
}
export interface Dashboard {
  metrics: DashboardMetrics;
  recent_workflows: Workflow[];
  recent_events: WatcherEvent[];
}
export interface ApiResponse<T> { success: true; data: T; message: string; }

