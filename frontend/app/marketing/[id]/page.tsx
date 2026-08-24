import { ReactNode } from "react";
import { BudgetEditor } from "@/components/BudgetEditor";
import { SidebarLayout } from "@/components/SidebarLayout";

export default async function MarketingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  
  const headerPill = (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', backgroundColor: '#fbeceb', color: '#b93126', padding: '6px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
      🔒 Restricted Data Access
    </span>
  );

  return (
    <SidebarLayout active="marketing" customHeaderPills={headerPill}>
      <div className="commandTitleRow" style={{ marginBottom: '10px' }}>
        <div>
          <h1 style={{ margin: '0 0 5px', fontSize: '2rem', letterSpacing: '-.045em' }}>Q3 Campaign Planner</h1>
          <p style={{ margin: '0', color: '#64646e', fontSize: '.9rem' }}>Allocate resources and orchestrate timeline for upcoming launch.</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="insightButton" style={{ background: 'white', color: '#333', border: '1px solid #ccc', boxShadow: 'none' }}>
            ⟳ Regenerate Strategy
          </button>
          <button className="insightButton" style={{ background: '#000' }}>
            ✓ Approve & Submit
          </button>
        </div>
      </div>
      <BudgetEditor id={id} />
    </SidebarLayout>
  );
}

