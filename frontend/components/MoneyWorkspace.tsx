"use client";
import { useCallback, useEffect, useState } from "react";
import { getWorkers, listWorkflows, request } from "@/lib/api";
import type { Worker, Workflow } from "@/lib/types";
import { formatNpr } from "@/lib/formatters";
import { EmptyState, ErrorState } from "./AsyncStates";
type Entry = { id:string; kind:string; amount:string; description:string; date:string; workflow_id:string|null; worker_id:string|null };
type Ledger = { entries:Entry[]; income:string; expenses:string; net:string };
export function MoneyWorkspace() {
  const [ledger,setLedger]=useState<Ledger|null>(null);
  const [workers,setWorkers]=useState<Worker[]>([]);
  const [workflows,setWorkflows]=useState<Workflow[]>([]);
  const [form,setForm]=useState({kind:"expense",amount:"",description:"",date:"",workflow_id:"",worker_id:""});
  const [error,setError]=useState(""); const [pending,setPending]=useState(false);
  const [message,setMessage]=useState("");
  const load=useCallback(async()=>{try{const [l,w,f]=await Promise.all([request<Ledger>("/money"),getWorkers(),listWorkflows()]);setLedger(l);setWorkers(w);setWorkflows(f);setError("");}catch(e){setError(e instanceof Error?e.message:"Unable to load money records");}},[]);
  useEffect(()=>{const t=setTimeout(()=>void load(),0);return()=>clearTimeout(t);},[load]);
  async function save(e:React.FormEvent){e.preventDefault();setPending(true);setMessage("");try{await request("/money",{method:"POST",body:JSON.stringify({...form,workflow_id:form.workflow_id||null,worker_id:form.worker_id||null})});setForm({...form,amount:"",description:""});await load();setMessage("Recorded successfully. This app does not send payments.");}catch(e){setError(e instanceof Error?e.message:"Unable to save transaction");}finally{setPending(false);}}
  const change=(key:keyof typeof form,value:string)=>setForm(f=>({...f,[key]:value}));
  return <><header className="pageTitle"><div><span>Actual money records · NPR</span><h1>Money</h1><p>Track money received and spent. AI estimates do not create transactions here.</p></div></header>
    {error&&<ErrorState message={error} retry={()=>void load()}/>}
    <section className="commandKpis">{[["Income recorded",ledger?.income],["Expenses recorded",ledger?.expenses],["Net recorded cash flow",ledger?.net]].map(([label,value])=><article key={label}><header>{label}</header><strong>{value===undefined?"—":formatNpr(Number(value))}</strong></article>)}</section>
    <p className="workspaceNotice">These totals include only the entries below. They are not your bank balance, payroll balance, or OpenRouter credit balance.</p>
    <form className="workspaceCard" onSubmit={save}><h2>Record a transaction</h2><div className="workspaceFormGrid">
      <label>Type<select value={form.kind} onChange={e=>change("kind",e.target.value)}><option value="expense">Expense</option><option value="income">Income</option></select></label>
      <label>Amount (NPR)<input required type="number" min="0.01" step="0.01" max="9999999999.99" value={form.amount} onChange={e=>change("amount",e.target.value)}/></label>
      <label>Date<input required type="date" value={form.date} onChange={e=>change("date",e.target.value)}/></label>
      <label>Description<input required minLength={3} maxLength={300} value={form.description} onChange={e=>change("description",e.target.value)}/></label>
      <label>Workflow (optional)<select value={form.workflow_id} onChange={e=>change("workflow_id",e.target.value)}><option value="">Company transaction</option>{workflows.map(w=><option key={w.id} value={w.id}>{w.title}</option>)}</select></label>
      <label>Employee (optional)<select value={form.worker_id} onChange={e=>change("worker_id",e.target.value)}><option value="">Not related to an employee</option>{workers.map(w=><option key={w.id} value={w.id}>{w.name}</option>)}</select></label>
    </div><button disabled={pending}>{pending?"Saving…":"Save transaction"}</button>{message&&<p role="status">{message}</p>}</form>
    {!ledger?.entries.length?<EmptyState title="No money recorded yet" message="Enter your own transactions above. There are no preloaded amounts."/>:<section className="workspaceCard tableScroll"><h2>Transaction history</h2><table><thead><tr><th>Date</th><th>Description</th><th>Type</th><th>Amount</th><th>Employee</th></tr></thead><tbody>{ledger.entries.map(e=><tr key={e.id}><td>{e.date}</td><td>{e.description}</td><td>{e.kind}</td><td>{formatNpr(Number(e.amount))}</td><td>{workers.find(w=>w.id===e.worker_id)?.name??"—"}</td></tr>)}</tbody></table></section>}
  </>;
}
