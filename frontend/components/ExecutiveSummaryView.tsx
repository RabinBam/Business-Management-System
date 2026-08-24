"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { ProgressBar } from "./charts/ProgressBar";
import {
  demoExecutiveSummary,
  demoReport,
  demoWatcherStatus,
} from "@/lib/demoData";
import { getWorkflow } from "@/lib/api";
import { formatNpr } from "@/lib/formatters";
import type { Workflow } from "@/lib/types";

function LiveExecutiveSummary({ id }: { id: string }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    getWorkflow(id)
      .then((result) => {
        if (active) setWorkflow(result);
      })
      .catch((reason) => {
        if (active) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Unable to load the executive summary.",
          );
        }
      });
    return () => {
      active = false;
    };
  }, [id]);

  if (error)
    return (
      <AppShell mode="real">
        <ErrorState message={error} />
      </AppShell>
    );
  if (!workflow)
    return (
      <AppShell mode="real">
        <LoadingSkeleton rows={5} />
      </AppShell>
    );
  const summary = workflow.executive_summary;
  if (!summary)
    return (
      <AppShell mode="real">
        <header className="pageTitle">
          <div>
            <span>Executive intelligence</span>
            <h1>{workflow.title}</h1>
            <p>Workflow status: {workflow.status.replaceAll("_", " ")}</p>
          </div>
        </header>
        <EmptyState
          title="Executive summary unavailable"
          message="The summary appears after management completes the final review."
        />
      </AppShell>
    );

  return (
    <AppShell mode="real">
      <header className="pageTitle">
        <div>
          <span>Completed workflow</span>
          <h1>{workflow.title}</h1>
          <p>{summary.overview}</p>
        </div>
        <div className="summaryActions">
          <Link href={`/workflows/${workflow.id}`}>View workflow</Link>
          <Link href="/">Start New Workflow</Link>
        </div>
      </header>
      <section className="executiveKpis">
        <article><span>Status</span><strong>{workflow.status}</strong></article>
        <article><span>Approved budget</span><strong>{formatNpr(workflow.budget)}</strong></article>
        <article><span>Deadline</span><strong>{workflow.deadline}</strong></article>
      </section>
      <div className="executiveGrid">
        <section className="summaryPanel">
          <header><h2>Major Work Completed</h2></header>
          <ol>{summary.major_work_completed.map((item) => <li key={item}>{item}</li>)}</ol>
        </section>
        <section className="summaryPanel">
          <header><h2>Business Results</h2></header>
          <dl>
            <div><dt>Financial summary</dt><dd>{summary.financial_summary}</dd></div>
            <div><dt>Sales prediction</dt><dd>{summary.sales_prediction}</dd></div>
            <div><dt>Marketing strategy</dt><dd>{summary.marketing_strategy}</dd></div>
          </dl>
        </section>
        <section className="summaryPanel recommendationsPanel">
          <header><h2>Management Recommendation</h2></header>
          <p>{summary.management_recommendation}</p>
          <h3>Major Risks</h3>
          {summary.major_risks.length ? (
            <ul>{summary.major_risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
          ) : (
            <p>No major risks were returned.</p>
          )}
        </section>
      </div>
    </AppShell>
  );
}

export function ExecutiveSummaryView({ id }: { id: string }) {
  if (id !== "demo") return <LiveExecutiveSummary id={id} />;
  const summary = demoExecutiveSummary;
  return (
    <AppShell mode="demo">
      <header className="pageTitle">
        <div>
          <span>Quarterly review</span>
          <h1>Q3 Executive Review</h1>
          <p>
            Comprehensive summary of business execution and strategic alignment.
          </p>
        </div>
        <div className="summaryActions">
          <button>⇩ Download PDF</button>
          <Link href="/">▷ Start New Workflow</Link>
        </div>
      </header>
      <section className="executiveKpis">
        <article>
          <span>Total Revenue</span>
          <strong>{formatNpr(summary.totalRevenue)}</strong>
          <small>↑ {summary.salesGrowth}%</small>
        </article>
        <article>
          <span>Active Workflows</span>
          <strong>{summary.activeWorkflows}</strong>
          <small>{summary.completedWorkflows} completed</small>
        </article>
        <article>
          <span>Marketing ROI</span>
          <strong>{summary.marketingRoi}%</strong>
          <small>{summary.marketingStatus}</small>
        </article>
        <article>
          <span>Decision Accuracy</span>
          <strong>{summary.decisionAccuracy}%</strong>
          <small>Management reviewed</small>
        </article>
      </section>
      <div className="executiveGrid">
        <section className="summaryPanel">
          <header>
            <h2>Workflow Portfolio</h2>
            <span>Current quarter</span>
          </header>
          {summary.workflowCompletion.map((item) => (
            <article key={item.name}>
              <div>
                <strong>{item.name}</strong>
                <span>{item.value}%</span>
              </div>
              <ProgressBar
                value={item.value}
                tone={item.value === 100 ? "green" : "blue"}
              />
            </article>
          ))}
        </section>
        <section className="summaryPanel">
          <header>
            <h2>Business &amp; System Insight</h2>
            <span>{demoWatcherStatus.active_incidents} open incident</span>
          </header>
          <dl>
            <div>
              <dt>Current sales</dt>
              <dd>{formatNpr(demoReport.sales_prediction.current_sales)}</dd>
            </div>
            <div>
              <dt>Predicted sales</dt>
              <dd>{formatNpr(demoReport.sales_prediction.predicted_sales)}</dd>
            </div>
            <div>
              <dt>Watcher state</dt>
              <dd>{demoWatcherStatus.state}</dd>
            </div>
            <div>
              <dt>Marketing status</dt>
              <dd>{summary.marketingStatus}</dd>
            </div>
          </dl>
        </section>
        <section className="summaryPanel recommendationsPanel">
          <header>
            <h2>Executive Recommendations</h2>
            <span>Management review</span>
          </header>
          <ol>
            {summary.recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        </section>
      </div>
    </AppShell>
  );
}
