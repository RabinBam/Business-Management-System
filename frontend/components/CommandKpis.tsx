"use client";

import { Bar, BarChart, ResponsiveContainer } from "recharts";
import { formatNpr } from "@/lib/formatters";
import type { Dashboard } from "@/lib/types";
import { KpiSparkline } from "./charts/KpiSparkline";
import { ProgressBar } from "./charts/ProgressBar";

export function CommandKpis({ dashboard }: { dashboard: Dashboard | null }) {
  const metrics = dashboard?.metrics;
  const totalBudget = metrics?.total_budget ?? 0;
  const plannedSpend = metrics?.planned_spend ?? 0;
  const growth = metrics?.predicted_growth_percent ?? 0;
  const budgetTrend = dashboard?.recent_workflows
    .slice()
    .reverse()
    .map((workflow, index) => ({ index, value: workflow.budget })) ?? [{ index: 0, value: 0 }];
  const growthHistory = budgetTrend.map((_, index) =>
    budgetTrend.length === 1 ? growth : (growth * (index + 1)) / budgetTrend.length,
  );

  return (
    <section className="commandKpis" aria-label="Live portfolio metrics">
      <article>
        <header><span>Total Portfolio Budget</span><small>{metrics?.workflow_count ?? 0} workflows</small></header>
        <strong>{formatNpr(totalBudget)}</strong>
        <div className="miniChart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={budgetTrend}>
              <Bar dataKey="value" fill="#6366f1" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </article>
      <article>
        <header>
          <span>Planned Spend</span>
          <small>{totalBudget ? Math.round((plannedSpend / totalBudget) * 100) : 0}%</small>
        </header>
        <strong>{formatNpr(plannedSpend)}</strong>
        <ProgressBar value={plannedSpend} max={totalBudget || 1} />
        <p>{formatNpr(metrics?.available_budget ?? 0)} available</p>
      </article>
      <article className="growthKpi">
        <header>
          <span>Predicted Growth</span>
          <small>{metrics?.completed_workflows ?? 0} completed</small>
        </header>
        <strong>{growth >= 0 ? "+" : ""}{growth.toFixed(1)}%</strong>
        <KpiSparkline data={growthHistory} />
      </article>
    </section>
  );
}
