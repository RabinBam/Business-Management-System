import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { ExecutiveObjectiveForm } from "@/components/ExecutiveObjectiveForm";
import { demoDashboard, demoWorkflow } from "@/lib/demoData";
import { formatDate, formatNpr } from "@/lib/formatters";

const stages = ["Executive Goal", "Segmentation", "Assignment", "Execution", "Review", "Reporting", "Marketing", "Final Review"];

export default function HomePage() {
  return <AppShell mode="demo">
    <header className="pageTitle"><div><span>Executive workspace</span><h1>Command Center</h1><p>Real-time intelligence and execution monitoring.</p></div><Link className="primaryButton" href="/reports/demo">✦ Generate Insight Report</Link></header>
    <section className="dashboardKpis"><article><span>Total Budget</span><strong>{formatNpr(demoDashboard.totalBudget)}</strong><small>{demoWorkflow.title}</small></article><article><span>Planned Spend</span><strong>{formatNpr(demoDashboard.plannedSpend)}</strong><small>{formatNpr(demoDashboard.remainingBudget)} remaining</small></article><article><span>Predicted Growth</span><strong>+{demoDashboard.predictedGrowth}%</strong><small>Forecast from reporting module</small></article><article><span>Current Status</span><strong>{demoWorkflow.status}</strong><small>Deadline {formatDate(demoWorkflow.deadline)}</small></article></section>
    <div className="commandBoard"><section className="commandPrimary"><ExecutiveObjectiveForm/><div className="overviewCard"><header><h2>Active Workflow Pipeline</h2><p>{demoWorkflow.objective}</p></header><ol>{stages.map((stage, index) => <li className={index < 3 ? "passed" : index === 3 ? "current" : ""} key={stage}><i>{index < 3 ? "✓" : index + 1}</i><span>{stage}</span></li>)}</ol></div></section><aside className="aiDecisionPanel"><header><span>◉</span><h2>AI Decision Intelligence</h2></header><div>{demoDashboard.decisionFeed.map((item, index) => <article className={index === 0 ? "active" : ""} key={item.title}><header><strong>{item.title}</strong><time>{item.time}</time></header><p>{item.message}</p></article>)}</div><footer><span>Prototype information</span><p>These centralized demo insights illustrate the complete Command Center before the backend exposes a decision-feed contract.</p></footer></aside></div>
  </AppShell>;
}
