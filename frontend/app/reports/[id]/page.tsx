import Link from "next/link";
import { FinancialSummary } from "@/components/FinancialSummary";
import { SidebarLayout } from "@/components/SidebarLayout";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <SidebarLayout active="reports">
      <div className="commandTitleRow">
        <div>
          <h1 style={{ margin: '0 0 5px', fontSize: '2rem', letterSpacing: '-.045em' }}>Financial Intelligence</h1>
          <p style={{ margin: '0', color: '#64646e', fontSize: '.9rem' }}>Q3 Budget Utilization & Sales Forecasting</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="insightButton" style={{ background: 'white', color: '#333', border: '1px solid #ccc', boxShadow: 'none' }}>
            <span style={{ fontSize: '1rem' }}>↓</span> Export PDF
          </button>
          <button className="insightButton">
            <span style={{ fontSize: '1rem' }}>✧</span> Generate AI Report
          </button>
        </div>
      </div>
      <FinancialSummary id={id} />
    </SidebarLayout>
  );
}
