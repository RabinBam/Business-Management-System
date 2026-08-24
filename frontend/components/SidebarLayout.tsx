import Link from "next/link";
import { ReactNode } from "react";

export function SidebarLayout({ children, active, customHeaderPills }: { children: ReactNode, active: string, customHeaderPills?: ReactNode }) {
  return (
    <div className="commandCenter">
      <aside className="commandSidebar">
        <div className="profileBlock">
          <div className="profileAvatar" style={{ backgroundImage: 'url(https://i.pravatar.cc/150?img=47)', backgroundSize: 'cover' }}></div>
          <div><strong>Decision Intelligence</strong><span>v1.0</span></div>
        </div>
        <nav>
          <Link href="/" className={active === 'command' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            Command Center
          </Link>
          <Link href="/workflows/1" className={active === 'workflow' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><line x1="6" y1="9" x2="6" y2="21"></line></svg>
            Workflow
          </Link>
          <Link href="/" className={active === 'workers' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            Workers
          </Link>
          <Link href="/reports/1" className={active === 'reports' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
            Reports
          </Link>
          <Link href="/marketing/1" className={active === 'marketing' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 11l18-5v12L3 14v-3z"></path><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"></path></svg>
            Marketing
          </Link>
          <Link href="/watcher" className={active === 'watcher' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            Watcher
          </Link>
          <Link href="/" className={active === 'executive' ? 'active' : ''}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            Executive Summary
          </Link>
        </nav>
      </aside>
      <div className="commandWorkspace">
        <header className="commandHeader">
          <strong>Kathmandu Digital Pvt. Ltd.</strong>
          <div style={{ display: 'flex', gap: '10px' }}>
            {customHeaderPills}
            <span className="healthPill"><i></i><b>Healthy</b></span>
          </div>
        </header>
        <main className="commandContent" style={{ minHeight: 'calc(100vh - 72px)', margin: '0' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
