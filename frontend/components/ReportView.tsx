"use client";
import Link from "next/link";
import {useEffect,useState} from "react";
import {AppShell} from "./AppShell";
import {getReport} from "@/lib/api";
import type {Report} from "@/lib/types";
import {formatNpr} from "@/lib/formatters";
import {EmptyState,ErrorState,LoadingSkeleton} from "./AsyncStates";
import {FinancialReportDownloadButton} from "./reports/FinancialReportExport";
import {ForecastChart} from "./charts/ForecastChart";
export function ReportView({id}:{id:string}){
 const [report,setReport]=useState<Report|null>(null);const [error,setError]=useState("");
 useEffect(()=>{let active=true;getReport(id).then(r=>{if(active)setReport(r);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[id]);
 if(error)return <AppShell><ErrorState message={error}/><Link href={`/workflows/${id}`}>Return to workflow</Link></AppShell>;
 if(!report)return <AppShell><LoadingSkeleton rows={3}/></AppShell>;
 const f=report.financial;const p=report.sales_prediction;const available=p.method!=="unavailable";
 return <AppShell><header className="pageTitle"><div><span>Finance team · workflow {id}</span><h1>Financial plan</h1><p>Budget allocations and revenue forecasts based on your inputs.</p></div><FinancialReportDownloadButton className="primaryButton" report={report} rows={[]} datasetName="User-entered workflow data"/></header>
 <section className="commandKpis"><article><header>Approved planning budget</header><strong>{formatNpr(f.total_budget)}</strong></article><article><header>Estimated task allocation</header><strong>{formatNpr(f.planned_spend)}</strong></article><article><header>Available for marketing</header><strong>{formatNpr(f.remaining_budget)}</strong></article></section>
 <section className="workspaceNotice"><strong>Finance handoff</strong><p>Task allocations reserve 60% of the budget, weighted by task difficulty. These are estimates, not payroll or money already spent. Marketing must remain inside the remaining budget. Verify estimates before committing funds.</p><div className="contextLinks"><Link href="/money">Record actual income and expenses →</Link><Link href="/tasks">Finance team tasks & notes →</Link></div></section>
 {available?<section className="workspaceCard"><h2>Next-month revenue forecast</h2><p>Last month: {formatNpr(p.current_sales)} · Forecast: {formatNpr(p.predicted_sales)} · Growth: {p.growth_percent.toFixed(1)}%</p><p>Linear trend from the consecutive monthly revenue values entered at workflow creation. This is an estimate.</p><div style={{height:280}}><ForecastChart data={[{month:"Last month",historical:p.current_sales},{month:"Next month",forecast:p.predicted_sales}]}/></div></section>:<EmptyState title="No sales forecast yet" message="No sample revenue is used. Supply at least two consecutive monthly revenue amounts when creating a workflow to enable its forecast."/>}
 <section className="workspaceCard"><h2>Risks & finance notes</h2><ul>{report.risks.map(r=><li key={r}>{r}</li>)}</ul><ul>{report.recommendations.map(r=><li key={r}>{r}</li>)}</ul><Link href={`/executive-summary/${id}`}>CEO summary →</Link></section></AppShell>;
}
