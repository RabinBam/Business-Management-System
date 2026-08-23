import { WatcherPanel } from "@/components/WatcherPanel";
import { SidebarLayout } from "@/components/SidebarLayout";

export const dynamic = "force-dynamic";

export default function WatcherPage() {
  return (
    <SidebarLayout active="watcher">
      <WatcherPanel />
    </SidebarLayout>
  );
}
