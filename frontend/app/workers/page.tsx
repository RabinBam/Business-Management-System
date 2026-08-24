import { AppShell } from "@/components/AppShell";
import { WorkersView } from "@/components/WorkersView";
export default function WorkersPage() {
  return (
    <AppShell mode="real">
      <WorkersView />
    </AppShell>
  );
}
