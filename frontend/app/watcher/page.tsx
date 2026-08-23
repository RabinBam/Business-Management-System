import Link from "next/link";

import { WatcherPanel } from "@/components/WatcherPanel";

export const dynamic = "force-dynamic";

export default function WatcherPage() {
  return (
    <main className="shell">
      <nav className="topbar">
        <Link className="brand" href="/">
          <span className="brandMark">AF</span>
          <span>AegisFlow</span>
        </Link>
      </nav>
      <header className="pageHeader">
        <div className="eyebrow">Reliability layer</div>
        <h1>Watcher activity</h1>
        <p>Failures, retries, and recoveries appear here without giving an AI control of recovery policy.</p>
      </header>
      <WatcherPanel />
    </main>
  );
}

