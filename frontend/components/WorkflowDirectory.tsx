"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { listWorkflows } from "@/lib/api";
import type { Workflow } from "@/lib/types";
import { formatNpr } from "@/lib/formatters";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
export function WorkflowDirectory({ section="workflows", title="Workflows" }: {section?:string;title?:string}) {
  const [items,setItems]=useState<Workflow[]>([]);const [error,setError]=useState("");const [loading,setLoading]=useState(true);
  const load=useCallback(async()=>{try{setItems(await listWorkflows());setError("");}catch(e){setError(e instanceof Error?e.message:"Unable to load workflows");}finally{setLoading(false);}},[]);
  useEffect(()=>{const t=setTimeout(()=>void load(),0);return()=>clearTimeout(t);},[load]);
  return <><header className="pageTitle"><div><span>Saved work</span><h1>{title}</h1><p>Select a workflow to see its {section==="workflows"?"tasks and next steps":title.toLowerCase()}.</p></div><Link className="primaryButton" href="/">Create workflow</Link></header>
    {loading?<LoadingSkeleton rows={3}/>:error?<ErrorState message={error} retry={()=>void load()}/>:!items.length?<EmptyState title="Start with your first workflow" message="There are no saved workflows or sample values. Create an objective from Command Center."/>:<div className="assignmentList">{items.map(w=><Link className="workspaceCard workflowRow" key={w.id} href={`/${section}/${w.id}`}><div><h2>{w.title}</h2><p>{w.objective}</p><small>{w.execution_mode==="employee"?"Employee execution":"AI execution"} · Due {w.deadline}</small></div><div><strong>{w.status.replaceAll("_"," ")}</strong><p>Planning budget {formatNpr(w.budget)}</p><span>Open →</span></div></Link>)}</div>}
  </>;
}
