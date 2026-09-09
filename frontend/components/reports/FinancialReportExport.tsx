"use client";

import { useRef, useState } from "react";
import { demoFinancialRows, demoReport } from "@/lib/demoData";
import { deriveFinancialMetrics, type FinancialDataRow } from "@/lib/financialParser";
import { formatNpr } from "@/lib/formatters";
import type { Report } from "@/lib/types";
import { BudgetDonut } from "../charts/BudgetDonut";
import { ForecastChart } from "../charts/ForecastChart";
import { ProgressBar } from "../charts/ProgressBar";
import { ReportAnalytics } from "./ReportAnalytics";
import styles from "./FinancialReportExport.module.css";

export function FinancialReportDownloadButton({
  report = demoReport,
  rows = demoFinancialRows,
  datasetName = "Built-in demonstration dataset",
  className,
}: {
  report?: Report;
  rows?: FinancialDataRow[];
  datasetName?: string;
  className?: string;
}) {
  const rootRef = useRef<HTMLDivElement>(null);
  const [exporting, setExporting] = useState(false);
  const metrics = deriveFinancialMetrics(rows);
  const totalBudget = metrics?.latest.totalBudget ?? report.financial.total_budget;
  const expense = metrics?.latest.expense ?? report.financial.planned_spend;
  const remaining = totalBudget - expense;
  const currentRevenue = metrics?.latest.revenue ?? report.sales_prediction.current_sales;
  const predictedRevenue = report.sales_prediction.predicted_sales;
  const forecastAvailable = report.sales_prediction.method !== "unavailable";

  async function download() {
    if (!rootRef.current || exporting) return;
    setExporting(true);
    try {
      await new Promise((resolve) => window.setTimeout(resolve, 300));
      const [{ default: html2canvas }, { jsPDF }] = await Promise.all([
        import("html2canvas"),
        import("jspdf"),
      ]);
      const analytics = rootRef.current.querySelector('[aria-label="Financial analytics"]');
      const blocks = [
        ...rootRef.current.querySelectorAll<HTMLElement>("[data-pdf-section]"),
        ...(analytics
          ? [...analytics.querySelectorAll<HTMLElement>(":scope > div:first-child, :scope > div:last-child > article")]
          : []),
      ];
      const pdf = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
      const pageWidth = 210;
      const pageHeight = 297;
      const margin = 10;
      const usableWidth = pageWidth - margin * 2;
      let y = margin;
      let first = true;
      for (const block of blocks) {
        const canvas = await html2canvas(block, {
          scale: 1.6,
          backgroundColor: "#ffffff",
          logging: false,
          useCORS: true,
        });
        const height = (canvas.height * usableWidth) / canvas.width;
        if (!first && y + height > pageHeight - margin) {
          pdf.addPage();
          y = margin;
        }
        pdf.addImage(
          canvas.toDataURL("image/png"),
          "PNG",
          margin,
          y,
          usableWidth,
          Math.min(height, pageHeight - margin * 2),
          undefined,
          "FAST",
        );
        y += height + 5;
        first = false;
      }
      const suffix = (metrics?.latest.period ?? report.workflow_id).replace(/[^a-z0-9-]/gi, "-");
      pdf.save(`Byapari-Financial-Report-${suffix}.pdf`);
    } finally {
      setExporting(false);
    }
  }

  return (
    <>
      <button className={className} disabled={exporting} onClick={() => void download()}>
        {exporting ? "Preparing PDF…" : "⇩ Download PDF"}
      </button>
      <div className={styles.stage} ref={rootRef} aria-hidden="true">
        <header className={styles.heading} data-pdf-section>
          <span>Financial Intelligence</span><h1>Byapari Financial Report</h1>
          <p>Dataset: {datasetName} · Workflow: {report.workflow_id}{metrics ? ` · Records: ${metrics.rows.length} · Coverage: ${metrics.coverage}` : " · API-generated report"}</p>
        </header>
        <section className={styles.kpis} data-pdf-section>
          <article><span>Current Revenue</span><strong>{forecastAvailable ? formatNpr(currentRevenue) : "Not supplied"}</strong></article>
          <article><span>Total Budget</span><strong>{formatNpr(totalBudget)}</strong></article>
          <article><span>Planned Spend</span><strong>{formatNpr(expense)}</strong></article>
          <article><span>Remaining Budget</span><strong>{formatNpr(remaining)}</strong></article>
          <article><span>Predicted Revenue</span><strong>{forecastAvailable ? formatNpr(predictedRevenue) : "Unavailable"}</strong></article>
          <article><span>Predicted Growth</span><strong>{forecastAvailable ? `${report.sales_prediction.growth_percent.toFixed(1)}%` : "Unavailable"}</strong></article>
          <article><span>Budget Utilization</span><strong>{totalBudget ? (expense / totalBudget * 100).toFixed(1) : "0.0"}%</strong></article>
          <article><span>Forecast Method</span><strong>{report.sales_prediction.method.replaceAll("_", " ")}</strong></article>
        </section>
        <section className={styles.overview} data-pdf-section>
          <div><h2>Total Budget Utilization</h2><BudgetDonut used={expense} total={totalBudget} /></div>
          <div className={styles.categories}>
            <h2>{metrics ? "Category Breakdown" : "Financial Position"}</h2>
            {metrics ? metrics.categories.map((item) => (
              <article key={item.name}><div><span>{item.name} · {formatNpr(item.amount)}</span><strong>{item.percent.toFixed(1)}%</strong></div><ProgressBar value={item.percent} /></article>
            )) : (
              <><article><div><span>Planned spend</span><strong>{formatNpr(expense)}</strong></div><ProgressBar value={expense} max={totalBudget || 1} /></article><article><div><span>Available budget</span><strong>{formatNpr(remaining)}</strong></div></article></>
            )}
          </div>
        </section>
        {forecastAvailable && <section className="chartCard" data-pdf-section>
          <header><div><span>Sales Revenue Forecast</span><h2>{formatNpr(predictedRevenue)}</h2></div><small>{report.sales_prediction.method.replaceAll("_", " ")}</small></header>
          <div className={styles.forecast}><ForecastChart data={[{ month: "Current", historical: currentRevenue }, { month: "Predicted", forecast: predictedRevenue }]} /></div>
        </section>}
        {metrics && <ReportAnalytics rows={metrics.rows} />}
        <section className={styles.insights} data-pdf-section>
          <div><h2>Risks</h2>{report.risks.length ? <ul>{report.risks.map((item) => <li key={item}>{item}</li>)}</ul> : <p>No risks were returned.</p>}</div>
          <div><h2>AI Business Insight &amp; Recommendations</h2>{report.recommendations.length ? <ul>{report.recommendations.map((item) => <li key={item}>{item}</li>)}</ul> : <p>No recommendations were returned.</p>}</div>
        </section>
      </div>
    </>
  );
}
