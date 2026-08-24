"use client";

import { useEffect, useState } from "react";
import { getMarketingPlan, updateMarketingPlan } from "@/lib/api";
import type { MarketingPlan, BudgetAllocation } from "@/lib/types";

export function BudgetEditor({ id }: { id: string }) {
  const [plan, setPlan] = useState<MarketingPlan | null>(null);

  useEffect(() => {
    getMarketingPlan(id).then(setPlan).catch(() => {});
  }, [id]);

  const channels = [
    { name: "Social Media", icon: "🔗", amount: 85000, percent: 34, color: "#e8effc" },
    { name: "Influencers", icon: "👥", amount: 65000, percent: 26, color: "#e2e6eb" },
    { name: "Search (SEM)", icon: "🔍", amount: 50000, percent: 20, color: "#fcf4d9" },
    { name: "Content Marketing", icon: "📄", amount: 50000, percent: 20, color: "#fce9e8" }
  ];

  return (
    <div className="marketingPlannerGrid" style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(280px, 0.9fr)', gap: '20px', marginTop: '30px' }}>
      
      {/* Left Column */}
      <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '30px', backgroundColor: '#fff', boxShadow: '0 4px 20px rgba(0,0,0,0.02)' }}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'end', marginBottom: '35px' }}>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 5px' }}>Budget Allocation</h2>
            <div style={{ fontSize: '0.8rem', color: '#666' }}>Total Available: <span style={{ fontFamily: 'monospace' }}>$250,000</span></div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#555', textTransform: 'uppercase' }}>Allocated</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800 }}>$250,000</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '25px', marginBottom: '40px' }}>
          {channels.map((ch, i) => (
            <div key={i}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.85rem', fontWeight: 700 }}>
                  <div style={{ width: '28px', height: '28px', borderRadius: '6px', backgroundColor: ch.color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>
                    {ch.icon}
                  </div>
                  {ch.name}
                </div>
                <div style={{ fontSize: '0.85rem', fontFamily: 'monospace', color: '#555' }}>
                  ${ch.amount.toLocaleString()} <span style={{ color: '#999' }}>({ch.percent}%)</span>
                </div>
              </div>
              <div style={{ height: '4px', backgroundColor: '#f0f0f0', borderRadius: '2px', position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: `${ch.percent}%`, width: '12px', height: '12px', backgroundColor: '#000', borderRadius: '50%', transform: 'translate(-50%, -50%)', cursor: 'pointer' }}></div>
              </div>
            </div>
          ))}
        </div>

        <div style={{ border: '1px solid #e0def7', borderLeft: '4px solid #655ef5', borderRadius: '8px', padding: '16px', backgroundColor: '#fafaff' }}>
          <h4 style={{ fontSize: '0.75rem', fontWeight: 800, margin: '0 0 8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: '#655ef5' }}>✧</span> AI Recommendation
          </h4>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#444', lineHeight: 1.5 }}>
            Shifting 5% from Content to Search is predicted to yield a 12% higher ROAS based on current competitor bidding trends.
          </p>
        </div>

      </div>

      {/* Right Column - Execution Timeline */}
      <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '30px', backgroundColor: '#fff', boxShadow: '0 4px 20px rgba(0,0,0,0.02)' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 800, margin: '0 0 30px' }}>Execution Timeline</h2>
        
        <div style={{ position: 'relative', paddingLeft: '30px' }}>
          {/* Vertical Line */}
          <div style={{ position: 'absolute', left: '11px', top: '20px', bottom: '20px', width: '2px', backgroundColor: '#eaeaea' }}></div>
          
          <div style={{ position: 'relative', marginBottom: '30px' }}>
            <div style={{ position: 'absolute', left: '-30px', top: '5px', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #000', backgroundColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2 }}>
              <div style={{ width: '8px', height: '8px', backgroundColor: '#000', borderRadius: '50%' }}></div>
            </div>
            <div style={{ backgroundColor: '#f8f9fa', border: '1px solid #eaeaea', borderRadius: '8px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <strong style={{ fontSize: '0.85rem' }}>Asset Creation</strong>
                <span style={{ fontSize: '0.75rem', color: '#666', fontFamily: 'monospace' }}>Oct 1 - Oct 15</span>
              </div>
              <p style={{ margin: '0 0 12px', fontSize: '0.85rem', color: '#555', lineHeight: 1.5 }}>Finalize all ad creatives and influencer briefs.</p>
              <span style={{ display: 'inline-block', backgroundColor: '#e8effc', color: '#4b7bdd', padding: '4px 8px', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.05em' }}>IN PROGRESS</span>
            </div>
          </div>

          <div style={{ position: 'relative', marginBottom: '30px' }}>
            <div style={{ position: 'absolute', left: '-30px', top: '5px', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #ccc', backgroundColor: '#fff', zIndex: 2 }}></div>
            <div style={{ border: '1px dashed #eaeaea', borderRadius: '8px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <strong style={{ fontSize: '0.85rem', color: '#555' }}>Soft Launch</strong>
                <span style={{ fontSize: '0.75rem', color: '#888', fontFamily: 'monospace' }}>Oct 18</span>
              </div>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#888', lineHeight: 1.5 }}>Deploy search campaigns and initial social retargeting.</p>
            </div>
          </div>

          <div style={{ position: 'relative' }}>
            <div style={{ position: 'absolute', left: '-30px', top: '5px', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #ccc', backgroundColor: '#fff', zIndex: 2 }}></div>
            <div style={{ border: '1px dashed #eaeaea', borderRadius: '8px', padding: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <strong style={{ fontSize: '0.85rem', color: '#555' }}>Full Rollout</strong>
                <span style={{ fontSize: '0.75rem', color: '#888', fontFamily: 'monospace' }}>Nov 1</span>
              </div>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#888', lineHeight: 1.5 }}>Activate influencers and scale social spend to 100%.</p>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}
