import Link from "next/link";

import { ExecutiveObjectiveForm } from "@/components/ExecutiveObjectiveForm";
import { WatcherBadge } from "@/components/WatcherBadge";

export default function HomePage() {
  return (
    <main className="shell">
      <nav className="topbar" aria-label="Primary navigation">
        <Link className="brand" href="/">
          <span className="brandMark">AF</span>
          <span>AegisFlow</span>
        </Link>
        <div className="navActions">
          <Link href="/watcher">System activity</Link>
          <WatcherBadge />
        </div>
      </nav>

      <section className="hero">
        <div className="eyebrow">Executive command center</div>
        <h1>Turn one objective into accountable work.</h1>
        <p>
          Define the outcome, budget, and deadline. AegisFlow creates the workflow
          your managers and specialists can inspect, execute, and report on.
        </p>
      </section>

      <section className="commandGrid" aria-label="Create a workflow">
        <ExecutiveObjectiveForm />
        <aside className="briefPanel">
          <p className="panelLabel">Operating model</p>
          <ol className="operatingSteps">
            <li><span>01</span> Segment the objective</li>
            <li><span>02</span> Review and assign work</li>
            <li><span>03</span> Execute with visible controls</li>
            <li><span>04</span> Report to leadership</li>
          </ol>
          <div className="boundaryNote">
            <strong>Human authority stays visible.</strong>
            <span>Budgets, approvals, and recovery rules remain deterministic.</span>
          </div>
        </aside>
      </section>
    </main>
  );
}

