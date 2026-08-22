"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { StatusBadge } from "./StatusBadge";
import { WorkflowPipeline } from "./WorkflowPipeline";
import { TaskCard } from "./TaskCard";
import { getTasks, getWorkflow } from "@/lib/api";
import { formatDate, formatDateTime, formatNpr } from "@/lib/formatters";
import type { Task, Workflow } from "@/lib/types";

export function WorkflowView({ id }: { id: string }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null); const [tasks, setTasks] = useState<Task[]>([]); const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  const load = useCallback(async () => { try { const [nextWorkflow, nextTasks] = await Promise.all([getWorkflow(id), getTasks(id)]); setWorkflow(nextWorkflow); setTasks(nextTasks); setError(""); } catch (reason) { setError(reason instanceof Error ? reason.message : "Unable to load workflow."); } finally { setLoading(false); } }, [id]);
  useEffect(() => { const timer = window.setTimeout(() => void load(), 0); return () => window.clearTimeout(timer); }, [load]);
  useEffect(() => { if (!workflow || ["COMPLETED", "FAILED"].includes(workflow.status)) return; const timer = window.setInterval(() => void load(), 2500); return () => window.clearInterval(timer); }, [load, workflow]);
  if (loading) return <AppShell><LoadingSkeleton rows={5}/></AppShell>;
  if (error || !workflow) return <AppShell><ErrorState message={error || "Workflow not found."} retry={() => void load()}/></AppShell>;
  return <AppShell><header className="pageTitle workflowPageTitle"><div><span>Workflow {workflow.id}</span><h1>{workflow.title}</h1><p>{workflow.objective}</p></div><StatusBadge status={workflow.status}/></header><section className="workflowFacts"><div><span>Budget</span><strong>{formatNpr(workflow.budget)}</strong></div><div><span>Deadline</span><strong>{formatDate(workflow.deadline)}</strong></div><div><span>Current stage</span><strong>{workflow.current_stage.replaceAll("_", " ")}</strong></div><div><span>Created</span><strong>{formatDateTime(workflow.created_at)}</strong></div></section><WorkflowPipeline status={workflow.status}/><div className="contextLinks"><Link href={`/reports/${id}`}>Financial report →</Link><Link href={`/marketing/${id}`}>Marketing plan →</Link></div><section className="contentSection"><header><div><span>Work register</span><h2>Tasks and assignments</h2></div><b>{tasks.length} tasks</b></header>{tasks.length ? <div className="taskGridNew">{tasks.map((task) => <TaskCard task={task} key={task.id}/>)}</div> : <EmptyState title="No tasks yet" message="Tasks will appear here once the Work Orchestrator completes segmentation."/>}</section></AppShell>;
}
