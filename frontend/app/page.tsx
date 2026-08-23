import Link from "next/link";
import type { ReactNode } from "react";

import { ExecutiveObjectiveForm } from "@/components/ExecutiveObjectiveForm";

type IconName = "grid" | "workflow" | "workers" | "reports" | "marketing" | "watcher" | "summary" | "sparkles" | "wallet" | "cash" | "trend" | "brain" | "download" | "check";

function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></>,
    workflow: <><rect x="3" y="4" width="6" height="6"/><rect x="15" y="14" width="6" height="6"/><path d="M9 7h4a3 3 0 0 1 3 3v4M7 10v7h8"/></>,
    workers: <><circle cx="9" cy="8" r="3"/><path d="M3 20c0-4 2-6 6-6s6 2 6 6M17 7h4M19 5v4M17 13h4"/></>,
    reports: <><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 17v-5M12 17V7M17 17v-8"/></>,
    marketing: <><path d="m3 11 14-6v14L3 13zM7 14l1 6h4l-2-5M20 8v8"/></>,
    watcher: <><path d="M3 20 9 12l4 3 8-11M16 4h5v5M3 4v5M1 6h4"/></>,
    summary: <><path d="M3 19 9 13l4 3 8-10"/><circle cx="3" cy="19" r="1"/><circle cx="9" cy="13" r="1"/><circle cx="13" cy="16" r="1"/><circle cx="21" cy="6" r="1"/></>,
    sparkles: <><path d="m12 3 1.3 3.7L17 8l-3.7 1.3L12 13l-1.3-3.7L7 8l3.7-1.3zM19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8zM5 13l.8 2.2L8 16l-2.2.8L5 19l-.8-2.2L2 16l2.2-.8z"/></>,
    wallet: <><path d="M4 6h15a2 2 0 0 1 2 2v11H4a2 2 0 0 1-2-2V6a3 3 0 0 1 3-3h12"/><path d="M16 11h5v5h-5a2.5 2.5 0 0 1 0-5z"/></>,
    cash: <><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M5 9V8h2M19 15v1h-2"/></>,
    trend: <><path d="m3 17 5-5 4 3 8-9M15 6h5v5"/></>,
    brain: <><path d="M9 4a3 3 0 0 0-5 2 3 3 0 0 0 0 6 3 3 0 0 0 2 5 3 3 0 0 0 3 3M15 4a3 3 0 0 1 5 2 3 3 0 0 1 0 6 3 3 0 0 1-2 5 3 3 0 0 1-3 3M9 4v16M15 4v16"/></>,
    download: <><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
  };
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

const navItems: { label: string; href: string; icon: IconName; active?: boolean }[] = [
  { label: "Command Center", href: "/", icon: "grid", active: true },
  { label: "Workflow", href: "/workflows/demo", icon: "workflow" },
  { label: "Workers", href: "#workforce", icon: "workers" },
  { label: "Reports", href: "/reports/demo", icon: "reports" },
  { label: "Marketing", href: "/marketing/demo", icon: "marketing" },
  { label: "Watcher", href: "/watcher", icon: "watcher" },
  { label: "Executive Summary", href: "#summary", icon: "summary" },
];

export default function HomePage() {
  return (
    <main className="commandCenter">
      <aside className="commandSidebar">
        <div className="profileBlock"><div className="profileAvatar">B</div><div><strong>Byapari</strong><span>Decision Intelligence</span><small>v1.0</small></div></div>
        <nav aria-label="Primary navigation">
          {navItems.map((item) => <Link key={item.label} href={item.href} className={item.active ? "active" : ""}><Icon name={item.icon}/><span>{item.label}</span></Link>)}
        </nav>
      </aside>

      <div className="commandWorkspace">
        <header className="commandHeader"><strong>Kathmandu Digital Pvt. Ltd.</strong><span className="healthPill"><i/> System Status: <b>Healthy</b></span></header>
        <div className="commandContent">
          <div className="commandTitleRow"><div><h1>Command Center</h1><p>Real-time intelligence and execution monitoring.</p></div><button className="insightButton" type="button"><Icon name="sparkles"/> Generate Insight Report</button></div>

          <div className="commandLayout">
            <div className="commandMainColumn">
              <section className="metricGrid" aria-label="Business metrics">
                <article className="metricCard"><Icon name="wallet" size={42}/><span>Total Budget</span><strong>NPR<br/>4.2M</strong><small className="positive">↑ 12%</small><div className="miniBars"><i/><i/><i/><i/><i/></div></article>
                <article className="metricCard"><Icon name="cash" size={42}/><span>Estimated Spend</span><strong>NPR<br/>1.8M</strong><small>− 0%</small><div className="spendTrack"><i/></div></article>
                <article className="metricCard growthCard"><Icon name="trend" size={34}/><span>Predicted Growth</span><strong>+24.5%</strong><small className="positive">High Confidence</small><svg viewBox="0 0 170 58" aria-label="Upward growth trend"><polyline points="2,47 25,39 45,50 66,28 88,37 109,13 130,29 151,5 169,15"/></svg></article>
              </section>
              <ExecutiveObjectiveForm />
              <section className="pipelineCard"><h2>Active Workflow Pipeline</h2><div className="pipelineSteps"><div className="done"><i><Icon name="check"/></i><strong>Formulation</strong><span>Completed</span></div><div className="current"><i><Icon name="brain"/></i><strong>Processing</strong><span>In Progress</span></div><div><i><Icon name="workers"/></i><strong>Assignment</strong><span>Pending</span></div><div><i><Icon name="summary"/></i><strong>Exec Summary</strong><span>Pending</span></div></div></section>
            </div>

            <aside className="decisionPanel">
              <div className="decisionHeading"><Icon name="brain" size={28}/><h2>AI Decision<br/>Intelligence</h2><i/></div>
              <div className="decisionFeed">
                <article className="active"><header><strong>Resource Optimization</strong><time>Just now</time></header><p>Reallocated NPR 150,000 from Marketing to Engineering based on Q2 velocity metrics.</p><a href="#trace">View Logic Trace →</a></article>
                <article><header><strong>Risk Alert</strong><time>14 mins ago</time></header><p>Detected potential bottleneck in Worker Group Alpha. Suggested adding 2 contingent resources.</p><div><button>Approve</button><button>Dismiss</button></div></article>
                <article><header><strong>Report Generated</strong><time>1 hr ago</time></header><p>Daily Executive Summary compiled. Key highlights: 3 workflows completed, NPR 45K saved.</p><button><Icon name="download" size={15}/> Download PDF</button></article>
                <article><header><strong>System</strong><time>3 hrs ago</time></header><p>Data sync completed with remote workers dataset.</p></article>
              </div>
            </aside>
          </div>
        </div>
      </div>
    </main>
  );
}
