"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { getReport } from "@/lib/api";
import { formatNpr } from "@/lib/formatters";
import type { Report } from "@/lib/types";
import {
  demoFinancialRows,
  demoReport,
} from "@/lib/demoData";
import { deriveFinancialMetrics, type FinancialDataRow } from "@/lib/financialParser";
import { BudgetDonut } from "./charts/BudgetDonut";
import { ForecastChart } from "./charts/ForecastChart";
import { ProgressBar } from "./charts/ProgressBar";
import { ReportAnalytics } from "./reports/ReportAnalytics";
import {
  FinancialDataSource,
  type FinancialDatasetSource,
} from "./FinancialDataSource";
type ActiveSource = "demo" | FinancialDatasetSource;
export function ReportView({ id }: { id: string }) {
  const isDemo = id === "demo";
  const [report, setReport] = useState<Report | null>(
      isDemo ? demoReport : null,
    ),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(!isDemo),
    [financialRows, setFinancialRows] = useState<FinancialDataRow[]>(
      isDemo ? demoFinancialRows : [],
    ),
    [source, setSource] = useState<ActiveSource>("demo"),
    [datasetName, setDatasetName] = useState("Built-in demonstration dataset");
  const load = useCallback(async () => {
    setLoading(true);
    try {
      setReport(await getReport(id));
      setError("");
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to load report.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);
  useEffect(() => {
    if (isDemo) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [isDemo, load]);
  const metrics = useMemo(() => deriveFinancialMetrics(financialRows), [financialRows]);
  if (loading)
    return (
      <AppShell>
        <LoadingSkeleton rows={5} />
      </AppShell>
    );
  if (error)
    return (
      <AppShell>
        <ErrorState message={error} retry={() => void load()} />
        <p className="availabilityHint">
          The report becomes available when the backend workflow reaches the
          reporting stage.
        </p>
      </AppShell>
    );
  if (!report)
    return (
      <AppShell>
        <EmptyState
          title="No report yet"
          message="The report will become available when the workflow reaches the reporting stage."
        />
      </AppShell>
    );
  const local = isDemo && metrics,
    totalBudget = local
      ? metrics.latest.totalBudget
      : report.financial.total_budget,
    expense = local ? metrics.latest.expense : report.financial.planned_spend,
    remaining = totalBudget - expense,
    revenue = local
      ? metrics.latest.revenue
      : report.sales_prediction.current_sales;
  function applyRows(
    rows: FinancialDataRow[],
    nextSource: FinancialDatasetSource,
    fileName?: string,
  ) {
    if (!isDemo) return;
    setFinancialRows(rows);
    setSource(nextSource);
    setDatasetName(
      fileName ??
        (nextSource === "sample"
          ? "2026 sample dataset"
          : "Manual financial entry"),
    );
  }
  return (
    <AppShell mode={isDemo ? "demo" : "real"}>
      <header className="pageTitle">
        <div>
          <span>Workflow {id}</span>
          <h1>Financial Intelligence</h1>
          <p>
            {local
              ? `${metrics.rows.length} row${metrics.rows.length === 1 ? "" : "s"} · ${metrics.split.yearly.length} yearly · ${metrics.split.monthly.length} monthly`
              : "API-generated workflow report"}
          </p>
        </div>
        <div className="reportActions">
          <FinancialDataSource demo={isDemo} onApply={applyRows} />
          <button className="secondaryButton">⇩ Export PDF</button>
        </div>
      </header>
      {local && (
        <div className="datasetBanner">
          <div>
            <strong>{datasetName}</strong>
            <span>Loaded locally for prototype analysis</span>
          </div>
          <small>Records: {metrics.rows.length} · Coverage: {metrics.coverage} · Yearly: {metrics.split.yearly.length} · Monthly: {metrics.split.monthly.length} · Monthly years: {metrics.monthlyYears.join(", ") || "None"}</small>
        </div>
      )}
      <section className="kpiGrid reportKpis">
        <article>
          <span>Total Budget</span>
          <strong>{formatNpr(totalBudget)}</strong>
        </article>
        <article>
          <span>Actual / Estimated Spend</span>
          <strong>{formatNpr(expense)}</strong>
        </article>
        <article>
          <span>Remaining Budget</span>
          <strong>{formatNpr(remaining)}</strong>
        </article>
        <article>
          <span>{local ? "Observed Growth" : "Predicted Growth"}</span>
          <strong>
            {local
              ? metrics.growth === null
                ? "N/A"
                : `${metrics.growth.toFixed(1)}%`
              : `${report.sales_prediction.growth_percent.toFixed(1)}%`}
          </strong>
          <small>
            {local ? "Period-over-period revenue" : "Backend prediction"}
          </small>
        </article>
      </section>
      <div className="reportGrid">
        <aside className="utilizationCard">
          <span>Total Budget Utilization</span>
          <BudgetDonut used={expense} total={totalBudget} />
          <dl>
            <div>
              <dt>Current Revenue</dt>
              <dd>{formatNpr(revenue)}</dd>
            </div>
            <div>
              <dt>Current Sales Units</dt>
              <dd>
                {local
                  ? metrics.latest.salesUnits.toLocaleString()
                  : "Not provided"}
              </dd>
            </div>
          </dl>
          {local && (
            <section className="categoryBreakdown">
              <h3>Latest Category Breakdown</h3>
              {metrics.categories.map((item) => (
                <article key={item.name}>
                  <div>
                    <span>
                      {item.name} · {formatNpr(item.amount)}
                    </span>
                    <strong>{item.percent.toFixed(1)}%</strong>
                  </div>
                  <ProgressBar value={item.percent} />
                </article>
              ))}
            </section>
          )}
        </aside>
        <section className="chartCard">
          <header>
            <div>
              <span>Sales Revenue Forecast</span>
              <h2>{formatNpr(revenue)}</h2>
            </div>
            <small>
              {local && source !== "demo"
                ? "Backend prediction integration required"
                : `Method: ${report.sales_prediction.method.replaceAll("_", " ")}`}
            </small>
          </header>
          {local && source !== "demo" ? (
            <div className="forecastNotice">AI forecast will be available after backend prediction integration.</div>
          ) : (
            <ForecastChart
              data={[
                {
                  month: "Current",
                  historical: report.sales_prediction.current_sales,
                },
                {
                  month: "Predicted",
                  forecast: report.sales_prediction.predicted_sales,
                },
              ]}
            />
          )}
        </section>
      </div>
      {local && <ReportAnalytics rows={metrics.rows} />}
      <aside className="insightsCard reportInsights">
        <section>
          <h2>Risks</h2>
          {source === "demo" || !isDemo ? (
            report.risks.length ? (
              <ul>
                {report.risks.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>No risks were returned.</p>
            )
          ) : (
            <p>AI-generated risks will appear after backend report analysis.</p>
          )}
        </section>
        <section>
          <h2>AI Business Insight &amp; Recommendation</h2>
          {source === "demo" || !isDemo ? (
            report.recommendations.length ? (
              <ul>
                {report.recommendations.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : (
              <p>No recommendations were returned.</p>
            )
          ) : (
            <p>AI recommendations will appear after backend report analysis.</p>
          )}
        </section>
      </aside>
    </AppShell>
  );
}
