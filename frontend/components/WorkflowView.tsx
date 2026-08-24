"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { StatusBadge } from "./StatusBadge";
import { WorkflowPipeline } from "./WorkflowPipeline";
import { TaskCard } from "./TaskCard";
import { getTasks, getWorkflow } from "@/lib/api";
import { formatDate, formatNpr } from "@/lib/formatters";
import type { Task, Workflow } from "@/lib/types";
import { demoTaskAssignees, demoTaskProgress, demoTasks, demoWorkflow } from "@/lib/demoData";

export function WorkflowView({ id }: { id: string }) {
  const isDemo = id === "demo";
  const [workflow, setWorkflow] = useState<Workflow | null>(isDemo ? demoWorkflow : null); const [tasks, setTasks] = useState<Task[]>(isDemo ? demoTasks : []); const [error, setError] = useState(""); const [loading, setLoading] = useState(!isDemo);
  const load = useCallback(async () => { try { const [nextWorkflow, nextTasks] = await Promise.all([getWorkflow(id), getTasks(id)]); setWorkflow(nextWorkflow); setTasks(nextTasks); setError(""); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load workflow."); } finally { setLoading(false); } }, [id]);
  useEffect(() => { if (isDemo) return; const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer); }, [isDemo, load]);
  useEffect(() => { if (isDemo || !workflow || ["COMPLETED", "FAILED"].includes(workflow.status)) return; const timer = window.setInterval(() => void load(), 2500); return () => window.clearInterval(timer); }, [isDemo, load, workflow]);
  if (loading) return <AppShell><LoadingSkeleton rows={5}/></AppShell>;
  if (error || !workflow) return <AppShell><ErrorState message={error || "Workflow not found."} retry={() => void load()}/></AppShell>;
  return <AppShell mode={isDemo ? "demo" : "real"}><header className="pageTitle workflowPageTitle"><div><span>Workflow {workflow.id}</span><h1>{workflow.title}</h1><p>{workflow.objective}</p></div><div className="completionBadge"><strong>{isDemo?62:"—"}%</strong><span>Overall Completion</span></div></header><section className="workflowFacts"><div><span>Status</span><StatusBadge status={workflow.status}/></div><div><span>Budget</span><strong>{formatNpr(workflow.budget)}</strong></div><div><span>Deadline</span><strong>{formatDate(workflow.deadline)}</strong></div><div><span>Current stage</span><strong>{workflow.current_stage.replaceAll("_", " ")}</strong></div></section><WorkflowPipeline status={workflow.status}/><div className="contextLinks"><Link href={`/reports/${id}`}>Financial report →</Link><Link href={`/marketing/${id}`}>Marketing plan →</Link><Link href={`/executive-summary/${id}`}>Executive summary →</Link></div><div className="workflowExecutionGrid"><section className="contentSection"><header><div><span>Work register</span><h2>Active Task Segmentation</h2></div><b>{tasks.length} tasks</b></header>{tasks.length ? <div className="taskGridNew">{tasks.map((task) => <TaskCard task={task} assignee={isDemo?demoTaskAssignees[task.id]:undefined} progress={isDemo?demoTaskProgress[task.id]:undefined} key={task.id}/>)}</div> : <EmptyState title="No tasks yet" message="Tasks will appear here once the Work Orchestrator completes segmentation."/>}</section>{isDemo&&<aside className="managementPanel"><header><span>◉</span><h2>Management AI Decisions</h2><p>Real-time rationale for workflow adjustments and resource allocation.</p></header><article><strong>Assignment rationale</strong><h3>Rohan Gurung assigned to segmentation</h3><p>Market research skills match the task requirements and current workload is available.</p></article><article><strong>Priority escalation</strong><h3>Customer segments marked critical</h3><p>Campaign Strategy Development depends on this output.</p></article><article><strong>Next action</strong><h3>Management review at 65%</h3><p>Validate the segment list before releasing approved context to Marketing.</p></article></aside>}</div></AppShell>;
}
