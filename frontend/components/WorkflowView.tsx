"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  cancelWorkflow,
  getManagementReviews,
  getTasks,
  getWorkerResults,
  getWorkflow,
  refineWorkflow,
  retryWorkflow,
  runWorkflow,
} from "@/lib/api";
import { demoTaskAssignees, demoTaskProgress, demoTasks, demoWorkflow } from "@/lib/demoData";
import { formatDate, formatNpr } from "@/lib/formatters";
import type { ManagementReview, Task, WorkerResult, Workflow } from "@/lib/types";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { StatusBadge } from "./StatusBadge";
import { TaskCard } from "./TaskCard";
import { WorkflowPipeline } from "./WorkflowPipeline";

const terminalStatuses = ["COMPLETED", "FAILED", "CANCELLED"];

export function WorkflowView({ id }: { id: string }) {
  const isDemo = id === "demo";
  const [workflow, setWorkflow] = useState<Workflow | null>(isDemo ? demoWorkflow : null);
  const [tasks, setTasks] = useState<Task[]>(isDemo ? demoTasks : []);
  const [results, setResults] = useState<WorkerResult[]>([]);
  const [reviews, setReviews] = useState<ManagementReview[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(!isDemo);
  const [action, setAction] = useState<"refine" | "run" | "retry" | "cancel" | null>(null);

  const load = useCallback(async () => {
    try {
      const [nextWorkflow, nextTasks, nextResults, nextReviews] = await Promise.all([
        getWorkflow(id), getTasks(id), getWorkerResults(id), getManagementReviews(id),
      ]);
      setWorkflow(nextWorkflow);
      setTasks(nextTasks);
      setResults(nextResults);
      setReviews(nextReviews);
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load workflow.");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (isDemo) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [isDemo, load]);
  useEffect(() => {
    if (isDemo || !workflow || terminalStatuses.includes(workflow.status)) return;
    const timer = window.setInterval(() => void load(), 2500);
    return () => window.clearInterval(timer);
  }, [isDemo, load, workflow]);

  const completion = useMemo(() => {
    if (workflow?.status === "COMPLETED") return 100;
    if (!tasks.length) return 0;
    return Math.round(tasks.reduce((sum, task) => sum + (task.status === "COMPLETED" ? 100 : task.status === "RUNNING" ? 50 : 0), 0) / tasks.length);
  }, [tasks, workflow]);

  async function perform(nextAction: NonNullable<typeof action>) {
    if (!workflow || action) return;
    setAction(nextAction);
    setError("");
    try {
      let updated: Workflow;
      if (nextAction === "refine") updated = await refineWorkflow(workflow.id);
      else if (nextAction === "cancel") updated = await cancelWorkflow(workflow.id);
      else if (nextAction === "retry") {
        await retryWorkflow(workflow.id);
        updated = await runWorkflow(workflow.id);
      } else updated = await runWorkflow(workflow.id);
      setWorkflow(updated);
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Workflow action failed.");
    } finally {
      setAction(null);
    }
  }

  if (loading) return <AppShell><LoadingSkeleton rows={5} /></AppShell>;
  if (error && !workflow) return <AppShell><ErrorState message={error} retry={() => void load()} /></AppShell>;
  if (!workflow) return <AppShell><ErrorState message="Workflow not found." /></AppShell>;

  const canCancel = !terminalStatuses.includes(workflow.status);
  return (
    <AppShell mode={isDemo ? "demo" : "real"}>
      <header className="pageTitle workflowPageTitle">
        <div><span>Workflow {workflow.id}</span><h1>{workflow.title}</h1><p>{workflow.objective}</p></div>
        <div className="completionBadge"><strong>{completion}%</strong><span>Overall Completion</span></div>
      </header>
      {error && <p className="inlineError" role="alert">{error}</p>}
      {workflow.failure && <p className="inlineError" role="alert">{workflow.failure.message}</p>}
      <section className="workspaceNotice"><strong>What happens next</strong><p>{workflow.status === "COMPLETED" ? "The workflow is complete. Review the deliverables, report, and executive summary." : workflow.status === "FAILED" ? "Resolve the error above, then retry the workflow." : workflow.execution_mode === "employee" && workflow.status === "EXECUTING" ? "Employees submit their assigned work in Employee workspace. Once all work is submitted, select Review submitted work." : workflow.status === "CREATED" ? "Prepare tasks to let AI plan the objective and assign the existing workforce." : "The current stage is shown below. Use the action button to continue."}</p><Link href="/employees">Employee workspace →</Link><p>Task costs are planning estimates allocated from 60% of the objective budget. Record actual payments separately in Money.</p></section>
      {!isDemo && (
        <div className="workflowActions">
          {workflow.status === "CREATED" && <button disabled={Boolean(action)} onClick={() => void perform("refine")}>{action === "refine" ? "Preparing…" : "Prepare Tasks"}</button>}
          {workflow.status !== "COMPLETED" && workflow.status !== "CANCELLED" && workflow.status !== "FAILED" && <button disabled={Boolean(action) || (workflow.execution_mode === "employee" && workflow.status === "EXECUTING" && results.length < tasks.length)} onClick={() => void perform("run")}>{action === "run" ? "Running…" : workflow.execution_mode === "employee" && workflow.status === "EXECUTING" ? "Review submitted work" : "Continue workflow"}</button>}
          {workflow.status === "FAILED" && <button disabled={Boolean(action)} onClick={() => void perform("retry")}>{action === "retry" ? "Retrying…" : "Retry Workflow"}</button>}
          {canCancel && <button className="dangerAction" disabled={Boolean(action)} onClick={() => void perform("cancel")}>{action === "cancel" ? "Cancelling…" : "Cancel"}</button>}
        </div>
      )}
      <section className="workflowFacts">
        <div><span>Status</span><StatusBadge status={workflow.status} /></div>
        <div><span>Budget</span><strong>{formatNpr(workflow.budget)}</strong></div>
        <div><span>Deadline</span><strong>{formatDate(workflow.deadline)}</strong></div>
        <div><span>Current stage</span><strong>{workflow.current_stage.replaceAll("_", " ")}</strong></div>
      </section>
      <WorkflowPipeline status={workflow.status} />
      <div className="contextLinks">
        <Link href={`/reports/${id}`}>Financial report →</Link>
        <Link href={`/marketing/${id}`}>Marketing plan →</Link>
        <Link href={`/executive-summary/${id}`}>Executive summary →</Link>
      </div>
      <div className="workflowExecutionGrid">
        <section className="contentSection">
          <header><div><span>Work register</span><h2>Task Segmentation</h2></div><b>{tasks.length} tasks</b></header>
          {tasks.length ? (
            <div className="taskGridNew">
              {tasks.map((task) => (
                <TaskCard
                  task={task}
                  assignee={isDemo ? demoTaskAssignees[task.id] : task.assigned_worker_name ?? undefined}
                  progress={isDemo ? demoTaskProgress[task.id] : task.status === "COMPLETED" ? 100 : task.status === "RUNNING" ? 50 : 0}
                  key={task.id}
                />
              ))}
            </div>
          ) : <EmptyState title="No tasks yet" message="Prepare or run the workflow to create its task plan." />}
        </section>
        {!isDemo && (results.length > 0 || reviews.length > 0) && (
          <aside className="managementPanel">
            <header><span>◉</span><h2>Management Decisions</h2><p>Verified worker outputs and management review records.</p></header>
            {reviews.map((review) => (
              <article key={`${review.task_id}-${review.decision}`}>
                <strong>{review.decision.replaceAll("_", " ")} · {review.task_id}</strong>
                <h3>{review.feedback}</h3>
                {review.revision_instructions.length > 0 && <p>{review.revision_instructions.join(" · ")}</p>}
              </article>
            ))}
            {results.map((result) => (
              <article key={result.task_id}>
                <strong>Worker output · {result.task_id}</strong>
                <h3>{result.summary}</h3><p>Recorded cost: {formatNpr(result.cost)}</p>
                {typeof result.output.deliverable === "string" && (
                  <details><summary>Read deliverable</summary><p style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere" }}>{result.output.deliverable}</p></details>
                )}
                {result.evidence.length > 0 && <ul>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul>}
                {Array.isArray(result.output.limitations) && result.output.limitations.length > 0 && <p>Limitations: {result.output.limitations.map(String).join(" · ")}</p>}
              </article>
            ))}
          </aside>
        )}
      </div>
    </AppShell>
  );
}
