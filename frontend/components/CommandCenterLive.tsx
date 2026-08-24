"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { getDashboard } from "@/lib/api";
import type { Dashboard, WorkflowStatus } from "@/lib/types";
import { CommandKpis } from "./CommandKpis";
import { ExecutiveObjectiveForm } from "./ExecutiveObjectiveForm";

const stages: Array<{ label: string; status: WorkflowStatus }> = [
  { label: "Executive Goal", status: "CREATED" },
  { label: "Segmentation", status: "SEGMENTING" },
  { label: "Assignment", status: "ASSIGNING" },
  { label: "Execution", status: "EXECUTING" },
  { label: "Review", status: "REVIEWING" },
  { label: "Reporting", status: "REPORTING" },
  { label: "Marketing", status: "MARKETING" },
  { label: "Final Review", status: "FINAL_REVIEW" },
];
const statusOrder: WorkflowStatus[] = [
  "CREATED", "SEGMENTING", "ASSIGNING", "EXECUTING", "REVIEWING",
  "REPORTING", "MARKETING", "FINAL_REVIEW", "COMPLETED",
];

function eventTime(value: string) {
  return new Intl.DateTimeFormat("en", { hour: "2-digit", minute: "2-digit" }).format(
    new Date(value),
  );
}

export function CommandCenterLive() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const load = useCallback(async () => {
    try {
      setDashboard(await getDashboard());
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load live metrics.");
    }
  }, []);

  useEffect(() => {
    const initial = window.setTimeout(() => void load(), 0);
    const refresh = window.setInterval(() => void load(), 10_000);
    return () => {
      window.clearTimeout(initial);
      window.clearInterval(refresh);
    };
  }, [load]);

  const latest = dashboard?.recent_workflows[0];
  const activeIndex = latest ? statusOrder.indexOf(latest.status) : -1;

  return (
    <>
      <header className="pageTitle">
        <div>
          <span>Executive workspace</span>
          <h1>Command Center</h1>
          <p>Live portfolio intelligence, execution monitoring, and accountable automation.</p>
        </div>
        {latest ? (
          <Link className="primaryButton" href={`/workflows/${latest.id}`}>View Latest Workflow</Link>
        ) : (
          <Link className="primaryButton" href="/workers">View Workforce</Link>
        )}
      </header>
      {error && <p className="inlineError" role="alert">{error} Retrying automatically.</p>}
      <CommandKpis dashboard={dashboard} />
      <div className="commandBoard">
        <section className="commandPrimary">
          <ExecutiveObjectiveForm onCreated={() => void load()} />
          <div className="overviewCard">
            <header>
              <div>
                <h2>Latest Workflow Pipeline</h2>
                <p>{latest?.objective ?? "Create a workflow to begin live orchestration."}</p>
              </div>
              {latest && <Link href={`/workflows/${latest.id}`}>{latest.status.replaceAll("_", " ")} →</Link>}
            </header>
            <ol>
              {stages.map((stage, index) => {
                const stageIndex = statusOrder.indexOf(stage.status);
                const current = latest?.status === stage.status;
                const passed = latest?.status === "COMPLETED" || (activeIndex >= 0 && stageIndex < activeIndex);
                return (
                  <li className={passed ? "passed" : current ? "current" : ""} key={stage.label}>
                    <i>{passed ? "✓" : index + 1}</i><span>{stage.label}</span>
                  </li>
                );
              })}
            </ol>
          </div>
        </section>
        <aside className="aiDecisionPanel">
          <header><span>◉</span><h2>AI Decision Intelligence</h2></header>
          <div>
            {dashboard?.recent_events.length ? dashboard.recent_events.map((item, index) => (
              <article className={index === 0 && !item.resolved ? "active" : ""} key={`${item.created_at}-${index}`}>
                <header><strong>{item.event_type.replaceAll("_", " ")}</strong><time>{eventTime(item.created_at)}</time></header>
                <p>{item.message}</p>
              </article>
            )) : <article><strong>No decisions recorded yet</strong><p>Workflow events will appear here as the orchestrator advances.</p></article>}
          </div>
          <footer>
            <span>Live operational state</span>
            <p>{dashboard?.metrics.active_workflows ?? 0} active · {dashboard?.metrics.failed_workflows ?? 0} failed · {dashboard?.recent_events.filter((event) => !event.resolved).length ?? 0} open events</p>
          </footer>
        </aside>
      </div>
    </>
  );
}
