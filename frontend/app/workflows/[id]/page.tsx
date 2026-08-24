<<<<<<< HEAD
import { WorkflowView } from "@/components/WorkflowView";
export default async function WorkflowPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <WorkflowView id={id} />;
}
=======
import { notFound } from "next/navigation";

import { TaskCard } from "@/components/TaskCard";
import { WorkflowPipeline } from "@/components/WorkflowPipeline";
import { getTasks, getWorkflow } from "@/lib/api";
import { SidebarLayout } from "@/components/SidebarLayout";

export const dynamic = "force-dynamic";

export default async function WorkflowPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await Promise.all([getWorkflow(id), getTasks(id)]).catch(() => null);

  if (!result) {
    notFound();
  }

  const [workflow, tasks] = result;

  return (
    <SidebarLayout active="workflow">
      <header className="workflowHeader">
        <div>
          <div className="eyebrow">Workflow {workflow.id}</div>
          <h1>{workflow.title}</h1>
          <p>{workflow.objective}</p>
        </div>
        <div className="statusCard">
          <span>Current status</span>
          <strong>{workflow.status.replaceAll("_", " ")}</strong>
          <small>{workflow.current_stage.replaceAll("_", " ")}</small>
        </div>
      </header>

      <WorkflowPipeline status={workflow.status} />

      <section className="taskSection">
        <div className="sectionHeading">
          <div>
            <p className="panelLabel">Work register</p>
            <h2>Tasks and assignments</h2>
          </div>
          <span>{tasks.length} tasks</span>
        </div>
        {tasks.length > 0 ? (
          <div className="taskGrid">{tasks.map((task) => <TaskCard key={task.id} task={task} />)}</div>
        ) : (
          <div className="emptyState">
            <strong>The workflow contract is ready.</strong>
            <p>Person 1 can connect objective segmentation here; Person 2 can add assignment and execution.</p>
          </div>
        )}
      </section>
    </SidebarLayout>
  );
}
>>>>>>> frontend-shaira
