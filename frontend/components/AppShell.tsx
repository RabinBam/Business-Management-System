"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

function pathWorkflowId(pathname: string) {
  const match = pathname.match(
    /^\/(?:workflows|reports|marketing|executive-summary)\/([^/]+)/,
  );
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

export function AppShell({
  children,
  mode,
  workflowId,
}: {
  children: ReactNode;
  mode?: "demo" | "real";
  workflowId?: string;
}) {
  const pathname = usePathname();
  const pathId = workflowId ?? pathWorkflowId(pathname);
  const encodedId = pathId ? encodeURIComponent(pathId) : null;
  const [menuOpen, setMenuOpen] = useState(false);
  const links = [
    ["Command Center", "/", "▦"],
    ["AI Workforce", "/workers?demo=1", "♙"],
    ["Workflow", `/workflows/${encodedId ?? "demo"}`, "⌘"],
    ["Reports", `/reports/${encodedId ?? "demo"}`, "▥"],
    ["Marketing", `/marketing/${encodedId ?? "demo"}`, "⌁"],
    [
      "Watcher",
      encodedId ? `/watcher?workflow=${encodedId}` : "/watcher?demo=1",
      "⌁",
    ],
    ["Executive Summary", `/executive-summary/${encodedId ?? "demo"}`, "⌁"],
  ];
  const activeFor = (label: string) =>
    label === "Command Center"
      ? pathname === "/"
      : label === "AI Workforce"
        ? pathname.startsWith("/workers")
        : label === "Workflow"
          ? pathname.startsWith("/workflows")
          : label === "Reports"
            ? pathname.startsWith("/reports")
            : label === "Marketing"
              ? pathname.startsWith("/marketing")
              : label === "Watcher"
                ? pathname.startsWith("/watcher")
                : pathname.startsWith("/executive-summary");
  const demoMode = mode === "demo" || pathId === "demo";
  return (
    <main className={`appShell ${menuOpen ? "navOpen" : ""}`}>
      <button
        aria-controls="primary-sidebar"
        aria-expanded={menuOpen}
        aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
        className="menuButton"
        onClick={() => setMenuOpen((value) => !value)}
      >
        <i /><i /><i />
      </button>
      {menuOpen && <button aria-label="Close navigation menu" className="navScrim" onClick={() => setMenuOpen(false)} />}
      <aside className="sidebar" id="primary-sidebar">
        <Link className="brandBlock" href="/">
          <span>B</span>
          <div>
            <strong>Byapari</strong>
            <small>Decision Intelligence</small>
          </div>
        </Link>
        <nav aria-label="Primary navigation">
          {links.map(([label, href, icon]) => (
            <Link
              className={activeFor(label) ? "active" : ""}
              href={href}
              key={label}
              onClick={() => setMenuOpen(false)}
            >
              <b aria-hidden="true">{icon}</b>
              {label}
            </Link>
          ))}
        </nav>
        <small className="version">v1.0</small>
      </aside>
      <div className="appBody">
        <header className="topbarNew">
          <strong>Kathmandu Digital Pvt. Ltd.</strong>
          <span className={demoMode ? "demoMode" : ""}>
            <i />
            {demoMode ? "Prototype Mode" : "Workspace"}
          </span>
        </header>
        <div className="pageCanvas">{children}</div>
      </div>
    </main>
  );
}
