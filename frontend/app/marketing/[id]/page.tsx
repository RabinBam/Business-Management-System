<<<<<<< HEAD
import Link from "next/link";

export default async function MarketingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="centeredState">
      <span className="brandMark">AF</span>
      <p className="eyebrow">Workflow {id}</p>
      <h1>Marketing workspace ready</h1>
      <p>Person 3 owns validated plan data. Person 5 owns the human budget editor on this route.</p>
      <Link className="buttonLink" href={`/workflows/${id}`}>Back to workflow</Link>
    </main>
  );
}

=======
import Link from "next/link";
import { BudgetEditor } from "@/components/BudgetEditor";

export default async function MarketingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  
  return (
    <AppShell mode={id === "demo" ? "demo" : "real"}>
      <div className="pageTitle marketingTitle">
        <div>
          <span>Human-in-the-loop planning</span>
          <h1>Q3 Campaign Planner</h1>
          <p>Allocate resources and orchestrate the timeline for the upcoming launch.</p>
        </div>
        <div className="marketingActions">
          <button className="secondaryButton">
            ⟳ Regenerate Strategy
          </button>
          <button className="primaryButton">
            ✓ Approve & Submit
          </button>
        </div>
      </div>
      <BudgetEditor id={id} />
    </AppShell>
  );
}

>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
