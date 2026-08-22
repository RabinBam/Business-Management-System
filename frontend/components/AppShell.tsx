"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

function workflowId(pathname: string) {
  const match = pathname.match(/^\/(?:workflows|reports|marketing)\/([^/]+)/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const id = workflowId(pathname);
  const links = [
    ["Command Center", "/", "▦"],
    ["Workflow", id ? `/workflows/${id}` : "/", "⌘"],
    ["Reports", id ? `/reports/${id}` : "/", "▥"],
    ["Marketing", id ? `/marketing/${id}` : "/", "⌁"],
    ["Watcher", "/watcher", "⌁"],
  ];
  return <main className="appShell"><aside className="sidebar"><Link className="brandBlock" href="/"><span>B</span><div><strong>Byapari</strong><small>Decision Intelligence</small></div></Link><nav aria-label="Primary navigation">{links.map(([label, href, icon]) => { const active = href === "/" ? pathname === "/" : pathname.startsWith(href.split("/").slice(0, 2).join("/")); const disabled = !id && ["Workflow", "Reports", "Marketing"].includes(label); return <Link aria-disabled={disabled} className={`${active ? "active" : ""} ${disabled ? "disabled" : ""}`} href={href} key={label}><b aria-hidden="true">{icon}</b>{label}</Link>; })}</nav><small className="version">v1.0</small></aside><div className="appBody"><header className="topbarNew"><strong>Kathmandu Digital Pvt. Ltd.</strong><span><i/> System Online</span></header><div className="pageCanvas">{children}</div></div></main>;
}
