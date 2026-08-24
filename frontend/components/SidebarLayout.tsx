"use client";

import Link from "next/link";
import { ReactNode, useState } from "react";

type IconName = "grid" | "workflow" | "workers" | "reports" | "marketing" | "watcher" | "summary" | "sparkles" | "wallet" | "cash" | "trend" | "brain" | "download" | "check";

function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    grid: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></>,
    workflow: <><rect x="3" y="4" width="6" height="6"/><rect x="15" y="14" width="6" height="6"/><path d="M9 7h4a3 3 0 0 1 3 3v4M7 10v7h8"/></>,
    workers: <><circle cx="9" cy="8" r="3"/><path d="M3 20c0-4 2-6 6-6s6 2 6 6M17 7h4M19 5v4M17 13h4"/></>,
    reports: <><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 17v-5M12 17V7M17 17v-8"/></>,
    marketing: <><path d="m3 11 14-6v14L3 13zM7 14l1 6h4l-2-5M20 8v8"/></>,
    watcher: <><path d="M3 20 9 12l4 3 8-11M16 4h5v5M3 4v5M1 6h4"/></>,
    summary: <><path d="M3 19 9 13l4 3 8-10"/><circle cx="3" cy="19" r="1"/><circle cx="9" cy="13" r="1"/><circle cx="13" cy="16" r="1"/><circle cx="21" cy="6" r="1"/></>,
    sparkles: <><path d="m12 3 1.3 3.7L17 8l-3.7 1.3L12 13l-1.3-3.7L7 8l3.7-1.3zM19 14l.8 2.2L22 17l-2.2.8L19 20l-.8-2.2L16 17l2.2-.8zM5 13l.8 2.2L8 16l-2.2.8L5 19l-.8-2.2L2 16l2.2-.8z"/></>,
    wallet: <><path d="M4 6h15a2 2 0 0 1 2 2v11H4a2 2 0 0 1-2-2V6a3 3 0 0 1 3-3h12"/><path d="M16 11h5v5h-5a2.5 2.5 0 0 1 0-5z"/></>,
    cash: <><rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="12" cy="12" r="3"/><path d="M5 9V8h2M19 15v1h-2"/></>,
    trend: <><path d="m3 17 5-5 4 3 8-9M15 6h5v5"/></>,
    brain: <><path d="M9 4a3 3 0 0 0-5 2 3 3 0 0 0 0 6 3 3 0 0 0 2 5 3 3 0 0 0 3 3M15 4a3 3 0 0 1 5 2 3 3 0 0 1 0 6 3 3 0 0 1-2 5 3 3 0 0 1-3 3M9 4v16M15 4v16"/></>,
    download: <><path d="M12 3v12M7 10l5 5 5-5M4 20h16"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
  };
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>;
}

function navItems(workflowId?: string) {
  const id = workflowId ? encodeURIComponent(workflowId) : "demo";
  return [
    { label: "Command Center", href: "/", id: "command", icon: "grid" as const },
    { label: "Workflow", href: `/workflows/${id}`, id: "workflow", icon: "workflow" as const },
    { label: "Workers", href: "/workers?demo=1", id: "workers", icon: "workers" as const },
    { label: "Reports", href: `/reports/${id}`, id: "reports", icon: "reports" as const },
    { label: "Marketing", href: `/marketing/${id}`, id: "marketing", icon: "marketing" as const },
    {
      label: "Watcher",
      href: workflowId ? `/watcher?workflow=${id}` : "/watcher?demo=1",
      id: "watcher",
      icon: "watcher" as const,
    },
    { label: "Executive Summary", href: `/executive-summary/${id}`, id: "executive", icon: "summary" as const },
  ];
}

export function SidebarLayout({ children, active, customHeaderPills, workflowId }: { children: ReactNode, active: string, customHeaderPills?: ReactNode, workflowId?: string }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <div className={`commandCenter ${isMobileMenuOpen ? 'menu-open' : ''}`}>
      <aside className={`commandSidebar ${isMobileMenuOpen ? 'open' : ''}`}>
        <div className="profileBlock">
          <div className="profileAvatar">B</div>
          <div><strong>Byapari</strong><span>Decision Intelligence</span><small>v1.0</small></div>
        </div>
        <nav aria-label="Primary navigation">
          {navItems(workflowId).map((item) => (
            <Link key={item.label} href={item.href} className={active === item.id ? "active" : ""} onClick={() => setIsMobileMenuOpen(false)}>
              <Icon name={item.icon}/>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>
      
      {isMobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setIsMobileMenuOpen(false)}></div>
      )}

      <div className="commandWorkspace">
        <header className="commandHeader">
          <div className="headerLeft">
            <button className="hamburger-btn" aria-label="Toggle menu" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>
            <strong>Kathmandu Digital Pvt. Ltd.</strong>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            {customHeaderPills}
            <span className="healthPill"><i></i> System Status: <b>Healthy</b></span>
          </div>
        </header>
        <main className="commandContent" style={{ minHeight: 'calc(100vh - 72px)', margin: '0' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
