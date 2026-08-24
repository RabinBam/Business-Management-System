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
      <WatcherPanel demo={demo} />
    </AppShell>
  );
}
