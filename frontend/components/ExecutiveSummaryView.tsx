import Link from "next/link";
import { AppShell } from "./AppShell";
import { EmptyState } from "./AsyncStates";
import { ProgressBar } from "./charts/ProgressBar";
import {
  demoExecutiveSummary,
  demoReport,
  demoWatcherStatus,
} from "@/lib/demoData";
import { formatNpr } from "@/lib/formatters";
export function ExecutiveSummaryView({ id }: { id: string }) {
  if (id !== "demo")
    return (
      <AppShell mode="real">
        <header className="pageTitle">
          <div>
            <span>Executive intelligence</span>
            <h1>Executive Summary</h1>
            <p>Consolidated business performance and decision information.</p>
          </div>
        </header>
        <EmptyState
          title="Executive summary unavailable"
          message="A consolidated executive-summary API contract is required for real workflow data."
        />
      </AppShell>
    );
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
