"use client";

import { useEffect, useState } from "react";
import { getWatcherStatus } from "@/lib/api";
import type { WatcherStatus } from "@/lib/types";

export function WatcherPanel() {
  const [watcher, setWatcher] = useState<WatcherStatus | null>(null);

  useEffect(() => {
    getWatcherStatus().then(setWatcher).catch(() => {});
  }, []);

  return (
    <div style={{ marginTop: '30px' }}>
      
      {/* Top Banner */}
      <div style={{ position: 'relative', border: '1px solid #e0e0e0', borderRadius: '12px', padding: '24px 30px', backgroundColor: '#f9faf9', overflow: 'hidden', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '8px', backgroundColor: '#57b889' }}></div>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#555', marginBottom: '4px', textTransform: 'uppercase' }}>System Status</div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#319267', margin: '0 0 8px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            ALL SYSTEMS OPERATIONAL
            <span style={{ backgroundColor: '#57b889', color: '#fff', width: '28px', height: '28px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem' }}>✓</span>
          </h1>
          <div style={{ fontSize: '0.85rem', color: '#666' }}>Last checked: Just now. Uptime: 99.99%</div>
        </div>
        <div>
          <button style={{ backgroundColor: '#000', color: '#fff', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: 700, cursor: 'pointer' }}>Run Full Diagnostic</button>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '24px' }}>
        
        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '20px', backgroundColor: '#fff', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', right: '20px', color: '#57b889' }}>☁</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444', marginBottom: '16px' }}>Database Cluster</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>12ms</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: '#666' }}>Avg Latency</span>
            <span style={{ fontSize: '0.75rem', color: '#57b889', fontWeight: 700 }}>Healthy</span>
          </div>
        </div>

        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '20px', backgroundColor: '#fff', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', right: '20px', color: '#57b889' }}>⚙</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444', marginBottom: '16px' }}>Worker Engine</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>1,024</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: '#666' }}>Active Jobs</span>
            <span style={{ fontSize: '0.75rem', color: '#57b889', fontWeight: 700 }}>Optimal</span>
          </div>
        </div>

        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '20px', backgroundColor: '#fff', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', right: '20px', color: '#e8a931' }}>📡</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444', marginBottom: '16px' }}>API Gateway</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>450 req/s</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: '#666' }}>Traffic Load</span>
            <span style={{ fontSize: '0.75rem', color: '#e8a931', fontWeight: 700 }}>Elevated</span>
          </div>
        </div>

        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '20px', backgroundColor: '#fff', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '20px', right: '20px', color: '#655ef5' }}>✧</div>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444', marginBottom: '16px' }}>Cache Layer</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '20px' }}>98.2%</div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: '#666' }}>Hit Rate</span>
            <span style={{ fontSize: '0.75rem', color: '#655ef5', fontWeight: 700 }}>AI Optimized</span>
          </div>
        </div>

      </div>

      {/* Bottom Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: '24px' }}>
        
        {/* System Event Log */}
        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '24px', backgroundColor: '#fff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 800 }}>System Event Log</h2>
            <span style={{ color: '#888', cursor: 'pointer' }}>≡</span>
          </div>
          
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #eaeaea', color: '#777', textAlign: 'left' }}>
                <th style={{ padding: '12px 0', fontWeight: 600 }}>Timestamp</th>
                <th style={{ padding: '12px 0', fontWeight: 600 }}>Component</th>
                <th style={{ padding: '12px 0', fontWeight: 600 }}>Event</th>
                <th style={{ padding: '12px 0', fontWeight: 600, textAlign: 'right' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {watcher ? watcher.events.map((event, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #f5f5f5' }}>
                  <td style={{ padding: '16px 0', fontFamily: 'monospace', color: '#555' }}>
                    {new Date(event.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td style={{ padding: '16px 0', fontWeight: 600 }}>{event.component}</td>
                  <td style={{ padding: '16px 0', color: '#444' }}>{event.message}</td>
                  <td style={{ padding: '16px 0', textAlign: 'right' }}>
                    <span style={{ color: event.event_type.includes('Action') ? '#655ef5' : event.event_type.includes('Success') ? '#279867' : '#d98f14', backgroundColor: event.event_type.includes('Action') ? '#f0efff' : 'transparent', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                      {event.event_type}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr style={{ borderBottom: '1px solid #f5f5f5' }}>
                  <td style={{ padding: '16px 0', fontFamily: 'monospace', color: '#555' }}>10:42:05 AM</td>
                  <td style={{ padding: '16px 0', fontWeight: 600 }}>API Gateway</td>
                  <td style={{ padding: '16px 0', color: '#444' }}>Rate limit adjusted</td>
                  <td style={{ padding: '16px 0', textAlign: 'right' }}><span style={{ color: '#655ef5', backgroundColor: '#f0efff', padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>AI Action</span></td>
                </tr>
              )}
            </tbody>

          </table>
        </div>

        {/* Failure Recovery Flow */}
        <div style={{ border: '1px solid #eaeaea', borderRadius: '12px', padding: '24px', backgroundColor: '#fff' }}>
          <h2 style={{ margin: '0 0 12px', fontSize: '1.1rem', fontWeight: 800 }}>Failure Recovery Flow</h2>
          <p style={{ fontSize: '0.85rem', color: '#666', lineHeight: 1.5, marginBottom: '30px' }}>Automated retry logic for external API dependencies.</p>
          
          <div style={{ position: 'relative', paddingLeft: '32px' }}>
            <div style={{ position: 'absolute', left: '11px', top: '15px', bottom: '15px', width: '2px', backgroundColor: '#eaeaea' }}></div>
            
            <div style={{ position: 'relative', marginBottom: '24px' }}>
              <div style={{ position: 'absolute', left: '-32px', top: '10px', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #aaa', backgroundColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 800, color: '#888', zIndex: 2 }}>!</div>
              <div style={{ border: '1px solid #eaeaea', borderRadius: '8px', padding: '16px', backgroundColor: '#f9f9f9' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '4px' }}>Initial Failure</div>
                <div style={{ fontSize: '0.75rem', color: '#666' }}>503 Service Unavailable</div>
              </div>
            </div>

            <div style={{ position: 'relative', marginBottom: '24px' }}>
              <div style={{ position: 'absolute', left: '-32px', top: '10px', width: '24px', height: '24px', borderRadius: '50%', border: '2px solid #d98f14', backgroundColor: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', color: '#d98f14', zIndex: 2 }}>↻</div>
              <div style={{ border: '1px solid #fbeec8', borderRadius: '8px', padding: '16px', backgroundColor: '#fdf9ee' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#9e670b', marginBottom: '4px' }}>Exponential Backoff</div>
                <div style={{ fontSize: '0.75rem', color: '#d98f14', fontWeight: 600 }}>Retrying in 2s, 4s, 8s...</div>
              </div>
            </div>

            <div style={{ position: 'relative' }}>
              <div style={{ position: 'absolute', left: '-32px', top: '10px', width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#279867', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', color: '#fff', zIndex: 2 }}>✓</div>
              <div style={{ border: '1px solid #c9ebd8', borderRadius: '8px', padding: '16px', backgroundColor: '#ebf7f0' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#176c45', marginBottom: '4px' }}>Recovery Successful</div>
                <div style={{ fontSize: '0.75rem', color: '#279867', fontWeight: 600 }}>Connection re-established</div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
}
