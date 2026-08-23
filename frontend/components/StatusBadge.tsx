import type { TaskStatus, WorkflowStatus } from "@/lib/types";

export function StatusBadge({ status }: { status: WorkflowStatus | TaskStatus }) {
  const tone = status === "COMPLETED" ? "success" : status === "FAILED" ? "danger" : status === "CREATED" || status === "PENDING" ? "neutral" : "active";
  return <span className={`statusBadge ${tone}`}><i/>{status.replaceAll("_", " ")}</span>;
}
