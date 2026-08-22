import { AppShell } from "@/components/AppShell"; import { WatcherPanel } from "@/components/WatcherPanel";
export default function WatcherPage() { return <AppShell><header className="pageTitle"><div><span>Reliability layer</span><h1>System Watcher</h1><p>Live failures, retries, validation events, and recoveries reported by FastAPI.</p></div></header><WatcherPanel/></AppShell>; }
