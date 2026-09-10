import { DemoResetButton } from "@/components/DemoResetButton";
import { AppShell } from "@/components/AppShell";
import { CommandCenterLive } from "@/components/CommandCenterLive";

export default function HomePage() {
  return (
    <AppShell mode="real">
      <DemoResetButton />
      <CommandCenterLive />
    </AppShell>
  );
}
