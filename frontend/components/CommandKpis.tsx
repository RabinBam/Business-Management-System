"use client";
import Link from "next/link";
import { formatNpr } from "@/lib/formatters";
import type { Dashboard } from "@/lib/types";
export function CommandKpis({dashboard}:{dashboard:Dashboard|null}) {
 const m=dashboard?.metrics;
 return <section className="commandKpis" aria-label="Live portfolio metrics">
 <article><header>Planning budgets</header><strong>{m?formatNpr(m.total_budget):"—"}</strong><p>Budgets entered for {m?.workflow_count??0} workflows. No payments implied.</p><Link href="/money">Actual money records →</Link></article>
 <article><header>Active workflows</header><strong>{m?.active_workflows??"—"}</strong><p>{m?.failed_workflows??0} need attention</p><Link href="/workflows">View all workflows →</Link></article>
 <article><header>Completed workflows</header><strong>{m?.completed_workflows??"—"}</strong><p>Finished through final review</p><Link href="/tasks">Task completion & handoffs →</Link></article>
 </section>;
}
