"use client";
import { useRef, useState } from "react";
import { demoFinancialRows, demoReport, demoSalesForecast } from "@/lib/demoData";
import { deriveFinancialMetrics } from "@/lib/financialParser";
import { formatNpr } from "@/lib/formatters";
import { BudgetDonut } from "../charts/BudgetDonut";
import { ForecastChart } from "../charts/ForecastChart";
import { ProgressBar } from "../charts/ProgressBar";
import { ReportAnalytics } from "./ReportAnalytics";
import styles from "./FinancialReportExport.module.css";

export function FinancialReportDownloadButton() {
  const rootRef = useRef<HTMLDivElement>(null);
  const [exporting,setExporting] = useState(false);
  const metrics = deriveFinancialMetrics(demoFinancialRows)!;
  const remaining = metrics.latest.totalBudget-metrics.latest.expense;
  async function download() {
    if (!rootRef.current || exporting) return;
    setExporting(true);
    try {
      await new Promise(resolve=>window.setTimeout(resolve,300));
      const [{default:html2canvas},{jsPDF}] = await Promise.all([import("html2canvas"),import("jspdf")]);
      const analytics = rootRef.current.querySelector('[aria-label="Financial analytics"]');
      const blocks = [
        ...rootRef.current.querySelectorAll<HTMLElement>("[data-pdf-section]"),
        ...(analytics ? [...analytics.querySelectorAll<HTMLElement>(":scope > div:first-child, :scope > div:last-child > article")] : []),
      ];
      const pdf = new jsPDF({unit:"mm",format:"a4",orientation:"portrait"});
      const pageWidth=210, pageHeight=297, margin=10, usableWidth=pageWidth-margin*2;
      let y=margin, first=true;
      for (const block of blocks) {
        const canvas=await html2canvas(block,{scale:1.6,backgroundColor:"#ffffff",logging:false,useCORS:true});
        const height=canvas.height*usableWidth/canvas.width;
        if (!first && y+height>pageHeight-margin) { pdf.addPage(); y=margin; }
        pdf.addImage(canvas.toDataURL("image/png"),"PNG",margin,y,usableWidth,Math.min(height,pageHeight-margin*2),undefined,"FAST");
        y+=height+5; first=false;
      }
      pdf.save(`Byapari-Financial-Report-${metrics.latest.year ?? metrics.latest.period}.pdf`);
    } finally { setExporting(false); }
  }
  return <>
    <button disabled={exporting} onClick={()=>void download()}>{exporting ? "Preparing PDF…" : "⇩ Download PDF"}</button>
    <div className={styles.stage} ref={rootRef} aria-hidden="true">
      <header className={styles.heading} data-pdf-section><span>Financial Intelligence</span><h1>Byapari Financial Report</h1><p>Dataset: Built-in demonstration dataset · Records: {metrics.rows.length} · Coverage: {metrics.coverage} · Reporting period: {metrics.latest.period}</p></header>
      <section className={styles.kpis} data-pdf-section>
        <article><span>Total Revenue</span><strong>{formatNpr(metrics.latest.revenue)}</strong></article><article><span>Total Budget</span><strong>{formatNpr(metrics.latest.totalBudget)}</strong></article><article><span>Total Expense</span><strong>{formatNpr(metrics.latest.expense)}</strong></article><article><span>Remaining Budget</span><strong>{formatNpr(remaining)}</strong></article><article><span>Gross Profit</span><strong>{formatNpr(metrics.latest.grossProfit ?? metrics.latest.revenue-metrics.latest.expense)}</strong></article><article><span>Revenue Growth</span><strong>{metrics.growth === null ? "N/A" : `${metrics.growth.toFixed(1)}%`}</strong></article><article><span>Budget Utilization</span><strong>{(metrics.latest.expense/metrics.latest.totalBudget*100).toFixed(1)}%</strong></article><article><span>Sales Units</span><strong>{metrics.latest.salesUnits.toLocaleString()}</strong></article>
      </section>
      <section className={styles.overview} data-pdf-section><div><h2>Total Budget Utilization</h2><BudgetDonut used={metrics.latest.expense} total={metrics.latest.totalBudget}/></div><div className={styles.categories}><h2>Category Breakdown</h2>{metrics.categories.map(item=><article key={item.name}><div><span>{item.name} · {formatNpr(item.amount)}</span><strong>{item.percent.toFixed(1)}%</strong></div><ProgressBar value={item.percent}/></article>)}</div></section>
      <section className="chartCard" data-pdf-section><header><div><span>Sales Revenue Forecast</span><h2>{formatNpr(demoReport.sales_prediction.predicted_sales)}</h2></div><small>Demonstration data · {demoReport.sales_prediction.method.replaceAll("_"," ")}</small></header><div className={styles.forecast}><ForecastChart data={demoSalesForecast}/></div></section>
      <ReportAnalytics rows={metrics.rows}/>
      <section className={styles.insights} data-pdf-section><div><h2>Risks</h2><ul>{demoReport.risks.map(item=><li key={item}>{item}</li>)}</ul></div><div><h2>AI Business Insight &amp; Recommendations</h2><ul>{demoReport.recommendations.map(item=><li key={item}>{item}</li>)}</ul></div></section>
    </div>
  </>;
}
