<<<<<<< HEAD
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

=======
import { AppShell } from "@/components/AppShell";
import { WatcherPanel } from "@/components/WatcherPanel";
export default async function WatcherPage({
  searchParams,
}: {
  searchParams: Promise<{ demo?: string }>;
}) {
  const demo = (await searchParams).demo === "1";
  return (
    <AppShell mode={demo ? "demo" : "real"}>
      <header className="pageTitle">
        <div>
          <span>Reliability layer</span>
          <h1>System Watcher</h1>
          <p>
            {demo
              ? "Prototype monitoring view with representative workflow events."
              : "Live failures, retries, validation events, and recoveries reported by FastAPI."}
          </p>
        </div>
      </header>
      <WatcherPanel/>
    </AppShell>
  );
}
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
