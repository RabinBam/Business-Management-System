import { AppShell } from "@/components/AppShell"; import { WorkersView } from "@/components/WorkersView";
export default async function WorkersPage({ searchParams }: { searchParams:Promise<{demo?:string}> }) { const demo=(await searchParams).demo!=="0"; return <AppShell mode={demo?"demo":"real"}><WorkersView demo={demo}/></AppShell>; }
