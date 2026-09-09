"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { listWorkflows, getTasks, getWorkers } from "@/lib/api";
import type { Task, Worker, Workflow } from "@/lib/types";
import { ProgressBar } from "./charts/ProgressBar";
import { EmptyState, ErrorState } from "./AsyncStates";
type Work = {workflow:Workflow;task:Task};
export function TaskManager() {
  const [items,setItems]=useState<Work[]>([]);const [workers,setWorkers]=useState<Worker[]>([]);const [selected,setSelected]=useState("all");const [error,setError]=useState("");const [ready,setReady]=useState(false);
  const load=useCallback(async()=>{try{const [flows,roster]=await Promise.all([listWorkflows(),getWorkers()]);const tasks=await Promise.all(flows.map(async workflow=>(await getTasks(workflow.id)).map(task=>({workflow,task}))));setItems(tasks.flat());setWorkers(roster);setError("");setReady(true);}catch(e){setError(e instanceof Error?e.message:"Unable to load tasks");}},[]);
  useEffect(()=>{const t=setTimeout(()=>void load(),0);const r=setInterval(()=>void load(),10000);return()=>{clearTimeout(t);clearInterval(r);};},[load]);
  const live=items.filter(i=>i.workflow.status!=="CANCELLED");const done=live.filter(i=>i.task.status==="COMPLETED").length;const submitted=live.filter(i=>i.task.status==="SUBMITTED").length;const percent=live.length?Math.round(done/live.length*100):0;
  const visible=items.filter(i=>selected==="all"||workers.find(w=>w.id===i.task.assigned_worker_id)?.department===selected);
  return <><header className="pageTitle"><div><span>Delivery control</span><h1>Tasks & team handoffs</h1><p>Follow the goal from department assignments to submitted work and completion.</p></div><Link className="primaryButton" href="/employees">Submit employee work</Link></header>
    <section className="commandKpis"><article><header>Completed tasks</header><strong>{ready?`${done} / ${live.length}`:"—"}</strong><ProgressBar value={percent}/><p>{percent}% complete · cancelled workflows excluded</p></article><article><header>Awaiting review</header><strong>{submitted}</strong><p>Employee submissions ready for management</p></article><article><header>Remaining work</header><strong>{live.length-done-submitted}</strong><p>Not submitted or needs revision</p></article></section>
    {error&&<ErrorState message={error} retry={()=>void load()}/>}
    <div className="workerToolbar"><div>{["all",...new Set(workers.map(w=>w.department))].map(d=><button key={d} className={selected===d?"active":""} onClick={()=>setSelected(d)}>{d==="all"?"All teams":d}</button>)}</div></div>
    {ready&&!visible.length?<EmptyState title="No tasks in this view" message="Prepare a workflow to generate distinct employee tasks and department notes."/>:<section className="assignmentList">{visible.map(({task:t,workflow:w})=><article className="workspaceCard" key={`${w.id}/${t.id}`}><div className="contextLinks"><Link href={`/workflows/${w.id}`}>{w.title} →</Link><span>{w.status==="CANCELLED"?"CANCELLED":t.status}</span></div><h2>{t.title}</h2><p><strong>{t.assigned_worker_name??"Unassigned"}</strong> · {t.required_role} · Due {w.deadline}</p><p>{t.employee_brief||t.description}</p><div className="workspaceNotice"><strong>Department handoff</strong><p>{t.handoff_notes||t.expected_output}</p><small>Prerequisites: {t.dependency_task_ids.join(", ")||"None"}</small></div><div className="contextLinks"><Link href={`/marketing/${w.id}`}>Marketing plan</Link><Link href={`/reports/${w.id}`}>Financial plan</Link><Link href={`/executive-summary/${w.id}`}>CEO summary</Link></div></article>)}</section>}
  </>;
}
