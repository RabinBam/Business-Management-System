"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getWorkers, request } from "@/lib/api";
import type { Worker, Workflow, Task, WorkerResult, ManagementReview } from "@/lib/types";
import { EmptyState, ErrorState } from "./AsyncStates";

type Assignment = { workflow: Workflow; task: Task; result: WorkerResult | null; review: ManagementReview | null; ready: boolean };

export function EmployeeWorkspace() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [selected, setSelected] = useState("");
  const [items, setItems] = useState<Assignment[]>([]);
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [pending, setPending] = useState("");
  const load = useCallback(async () => {
    try {
      setWorkers(await getWorkers());
      if (selected) setItems(await request<Assignment[]>(`/employees/${selected}/tasks`));
      setError("");
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to load assignments"); }
  }, [selected]);
  useEffect(() => { const t = window.setTimeout(() => void load(), 0); const r = window.setInterval(() => void load(), 10000); return () => { clearTimeout(t); clearInterval(r); }; }, [load]);
  async function submit(item: Assignment) {
    const key = `${item.workflow.id}/${item.task.id}`;
    setPending(key); setMessage(""); setError("");
    try {
      await request(`/employees/${selected}/tasks/${key}/submit`, { method: "POST", body: JSON.stringify({ deliverable: drafts[key] }) });
      setDrafts(d => ({...d, [key]: ""}));
      setMessage("Work submitted. Management can review it once all required tasks are submitted.");
      await load();
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to submit"); }
    finally { setPending(""); }
  }
  return <>
    <header className="pageTitle"><div><span>Employee workspace</span><h1>My assignments</h1><p>See your tasks, submit work, and read management feedback.</p></div></header>
    <section className="workspaceNotice"><label>View as employee<select value={selected} onChange={e => {setSelected(e.target.value); setItems([]); setMessage("");}}><option value="">Select your name</option>{workers.map(w => <option key={w.id} value={w.id}>{w.name} · {w.role}</option>)}</select></label><p>This is a local workspace selector, not a secure employee sign-in.</p></section>
    {error && <ErrorState message={error} retry={() => void load()} />}
    {message && <p role="status" className="workspaceNotice">{message}</p>}
    {!selected ? <EmptyState title="Choose an employee" message="The existing workforce roster is available above." /> : !items.length ? <EmptyState title="No assigned tasks" message="Create an employee workflow and prepare its task plan to assign work." /> : <section className="assignmentList">{items.map(item => {
      const key = `${item.workflow.id}/${item.task.id}`;
      const accepts = item.workflow.execution_mode === "employee" && item.workflow.status === "EXECUTING" && !item.result;
      return <article className="workspaceCard" key={key}>
        <div className="contextLinks"><Link href={`/workflows/${item.workflow.id}`}>{item.workflow.title} →</Link><span>{item.result ? "Submitted" : item.workflow.status === "CANCELLED" ? "Cancelled" : item.task.status}</span></div>
        <h2>{item.task.title}</h2><p>{item.task.description}</p>
        {item.task.employee_brief && <div className="workspaceNotice"><strong>Your AI briefing</strong><p>{item.task.employee_brief}</p></div>}
        {item.task.handoff_notes && <p><strong>Team handoff:</strong> {item.task.handoff_notes}</p>}
        <p><strong>Due:</strong> {item.workflow.deadline} · <strong>Expected output:</strong> {item.task.expected_output}</p>
        <ul>{item.task.acceptance_criteria.map(c => <li key={c}>{c}</li>)}</ul>
        {item.task.revision_instructions?.length ? <div className="workspaceNotice"><strong>Changes requested</strong><ul>{item.task.revision_instructions.map(c => <li key={c}>{c}</li>)}</ul></div> : null}
        {item.review && <p><strong>Management feedback:</strong> {item.review.feedback}</p>}
        {item.result && <details><summary>Read submitted work</summary><p className="deliverableText">{String(item.result.output.deliverable ?? item.result.summary)}</p></details>}
        {accepts && <form onSubmit={e => {e.preventDefault(); void submit(item);}}><label>Your completed work<textarea required minLength={10} maxLength={20000} rows={7} value={drafts[key] ?? ""} onChange={e => setDrafts(d => ({...d, [key]: e.target.value}))} placeholder="Write your deliverable, evidence, and any limitations." /></label>{!item.ready && <p>Waiting for prerequisite tasks: {item.task.dependency_task_ids.join(", ")}</p>}<button disabled={!!pending || !item.ready}>{pending === key ? "Submitting…" : "Submit for review"}</button></form>}
        {item.workflow.execution_mode !== "employee" && <p>AI execution workflow. Results are available to view here.</p>}
      </article>;
    })}</section>}
  </>;
}
