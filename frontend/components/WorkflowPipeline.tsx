import type { WorkflowStatus } from "@/lib/types";

const stages: Array<{ label: string; statuses: WorkflowStatus[] }> = [
  { label: "Created", statuses: ["CREATED"] }, { label: "Segmentation", statuses: ["SEGMENTING"] },
  { label: "Assignment", statuses: ["ASSIGNING"] }, { label: "Execution", statuses: ["EXECUTING"] },
  { label: "Review", statuses: ["REVIEWING"] }, { label: "Reporting", statuses: ["REPORTING"] },
  { label: "Marketing", statuses: ["MARKETING"] }, { label: "Final review", statuses: ["FINAL_REVIEW"] },
  { label: "Complete", statuses: ["COMPLETED"] },
];

const order: WorkflowStatus[] = [
  "CREATED", "SEGMENTING", "ASSIGNING", "EXECUTING", "REVIEWING",
  "REPORTING", "MARKETING", "FINAL_REVIEW", "COMPLETED",
];

export function WorkflowPipeline({ status }: { status: WorkflowStatus }) {
  const activeIndex = order.indexOf(status);
  return (
    <section className="pipeline" aria-label="Workflow progress">
      {stages.map((stage, index) => {
        const stageIndex = Math.min(...stage.statuses.map((item) => order.indexOf(item)));
        const state = status === "FAILED" || status === "CANCELLED" ? "waiting" : status === "COMPLETED" ? "complete" : stage.statuses.includes(status) ? "active" : stageIndex < activeIndex ? "complete" : "waiting";
        return (
          <div className={`pipelineStage ${state}`} key={stage.label}>
            <span>{state === "complete" ? "✓" : String(index + 1).padStart(2, "0")}</span>
            <strong>{stage.label}</strong>
          </div>
        );
      })}
    </section>
  );
}
