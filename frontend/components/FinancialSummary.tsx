"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, PieChart, Pie } from "recharts";

import { getReport } from "@/lib/api";
import type { Report } from "@/lib/types";

const data = [
  { name: 'Jan', value: 20 },
  { name: 'Feb', value: 35 },
  { name: 'Mar', value: 30 },
  { name: 'Apr', value: 45 },
  { name: 'May', value: 55 },
  { name: 'Jun', value: 65, isForecast: true },
  { name: 'Jul', value: 75, isForecast: true },
  { name: 'Aug', value: 50, isForecast: true },
];

export function FinancialSummary({ id }: { id: string }) {
  const [report, setReport] = useState<Report | null>(null);

  useEffect(() => {
    getReport(id).then(setReport).catch(() => {});
  }, [id]);

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px', marginTop: '30px' }}>
      
      {/* Left Column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '24px', backgroundColor: '#fff' }}>
          <h3 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#555', letterSpacing: '0.05em', marginBottom: '20px' }}>TOTAL BUDGET UTILIZATION</h3>
          
          <div style={{ position: 'relative', height: '220px', display: 'flex', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[{ value: 78 }, { value: 22 }]}
                  cx="50%" cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                >
                  <Cell fill="#000" />
                  <Cell fill="#f0f0f0" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
              <div style={{ fontSize: '2.2rem', fontWeight: 800 }}>78%</div>
              <div style={{ fontSize: '0.75rem', color: '#666', fontWeight: 600 }}>Consumed</div>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px', fontSize: '0.85rem' }}>
            <div>
              <div style={{ color: '#555', fontWeight: 600, marginBottom: '5px' }}>Total Allocated</div>
              <div style={{ fontWeight: 700 }}>NPR</div>
              <div style={{ fontSize: '1.2rem', fontFamily: 'monospace' }}>45,000,000</div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ color: '#555', fontWeight: 600, marginBottom: '5px' }}>Remaining</div>
              <div style={{ fontWeight: 700, color: '#655ef5' }}>NPR</div>
              <div style={{ fontSize: '1.2rem', color: '#655ef5', fontFamily: 'monospace' }}>9,900,000</div>
            </div>
          </div>
        </div>

        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '24px', backgroundColor: '#fff' }}>
          <h3 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#555', letterSpacing: '0.05em', marginBottom: '20px' }}>CATEGORY BREAKDOWN</h3>
          
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}>
              <span>Operations</span>
              <span style={{ fontFamily: 'monospace' }}>NPR 18.5M</span>
            </div>
            <div style={{ height: '8px', backgroundColor: '#eee', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '75%', height: '100%', backgroundColor: '#000' }}></div>
            </div>
          </div>
          
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}>
              <span>Marketing</span>
              <span style={{ fontFamily: 'monospace' }}>NPR 12.0M</span>
            </div>
            <div style={{ height: '8px', backgroundColor: '#eee', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '50%', height: '100%', backgroundColor: '#555' }}></div>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '8px' }}>
              <span>R&D</span>
              <span style={{ fontFamily: 'monospace' }}>NPR 4.6M</span>
            </div>
            <div style={{ height: '8px', backgroundColor: '#eee', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: '30%', height: '100%', backgroundColor: '#000' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '24px', backgroundColor: '#fff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '0.75rem', fontWeight: 700, color: '#555', letterSpacing: '0.05em', margin: 0 }}>SALES REVENUE FORECAST</h3>
            <div style={{ display: 'flex', gap: '16px', fontSize: '0.75rem', fontWeight: 600 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '12px', height: '12px', backgroundColor: '#000', borderRadius: '2px' }}></div> Historical</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><div style={{ width: '12px', height: '12px', backgroundColor: '#c7cbf5', borderRadius: '2px' }}></div> AI Forecast</div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '30px' }}>
            <div style={{ fontSize: '1.8rem', fontWeight: 800 }}>NPR 124.5M</div>
            <div style={{ backgroundColor: '#e2f5e9', color: '#176b52', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>~ +14.2% YoY</div>
          </div>

          <div style={{ height: '280px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#666' }} tickFormatter={(val) => val === 0 ? '0M' : 'M'} />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.isForecast ? '#c7cbf5' : (index === 4 ? '#000' : (index === 3 ? '#444' : '#b9b9b9'))} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={{ border: '1px solid #e0def7', borderLeft: '4px solid #655ef5', borderRadius: '12px', padding: '24px', backgroundColor: '#fff', boxShadow: '0 4px 20px rgba(101, 94, 245, 0.05)' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: '0 0 16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: '#655ef5' }}>✧</span> AI Strategic Insight
          </h3>
          <p style={{ color: '#333', lineHeight: 1.6, fontSize: '0.95rem', margin: '0 0 20px' }}>
            Based on historical trends and current budget burn rates, operations spending is projected to exceed allocation by Q4. Concurrently, AI forecasts predict a <span style={{ color: '#176b52' }}>14.2% surge</span> in sales revenue during June and July.
          </p>
          <div style={{ backgroundColor: '#f9f9fb', border: '1px solid #eaeaea', borderRadius: '8px', padding: '16px' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#555', marginBottom: '8px' }}>Recommendation</div>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#333', lineHeight: 1.5 }}>
              Reallocate NPR 2.5M from remaining R&D budget to Operations immediately to sustain projected sales volume without impacting core marketing initiatives.
            </p>
          </div>
        </div>

      </div>

    </div>
  );
}
