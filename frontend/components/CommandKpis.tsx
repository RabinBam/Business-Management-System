"use client";
import { Bar, BarChart, ResponsiveContainer } from "recharts";
import { demoCompanyMetrics } from "@/lib/demoData";
import { formatNpr } from "@/lib/formatters";
import { KpiSparkline } from "./charts/KpiSparkline";
import { ProgressBar } from "./charts/ProgressBar";
export function CommandKpis() {
  const metrics = demoCompanyMetrics;
  return (
    <section className="commandKpis">
      <article>
        <header>
          <span>Total Budget</span>
          <small>↑ 12%</small>
        </header>
        <strong>{formatNpr(metrics.totalBudget)}</strong>
        <div className="miniChart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={metrics.budgetTrend.map((value, index) => ({
                index,
                value,
              }))}
            >
              <Bar dataKey="value" fill="#6366f1" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>
      <article>
        <header>
          <span>Estimated Spend</span>
          <small>
            {Math.round((metrics.estimatedSpend / metrics.totalBudget) * 100)}%
          </small>
        </header>
        <strong>{formatNpr(metrics.estimatedSpend)}</strong>
        <ProgressBar value={metrics.estimatedSpend} max={metrics.totalBudget} />
        <p>
          {formatNpr(metrics.totalBudget - metrics.estimatedSpend)} available
        </p>
      </article>
      <article className="growthKpi">
        <header>
          <span>Predicted Growth</span>
          <small>{metrics.confidence}% confidence</small>
        </header>
        <strong>+{metrics.predictedGrowth}%</strong>
        <KpiSparkline data={metrics.growthHistory} />
      </article>
    </section>
  );
}
