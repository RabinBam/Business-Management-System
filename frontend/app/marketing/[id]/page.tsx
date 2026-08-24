import { AppShell } from "@/components/AppShell";
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

