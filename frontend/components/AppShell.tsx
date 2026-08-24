"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

function workflowId(pathname: string) {
  const match = pathname.match(/^\/(?:workflows|reports|marketing)\/([^/]+)/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

export function AppShell({
  children,
  mode,
}: {
  children: ReactNode;
  mode?: "demo" | "real";
}) {
  const pathname = usePathname();
  const pathId = workflowId(pathname);
  const [savedId, setSavedId] = useState<string | null>(null);
  useEffect(() => {
    const timer = window.setTimeout(
      () => setSavedId(window.localStorage.getItem("byapari:lastWorkflowId")),
      0,
    );
    return () => window.clearTimeout(timer);
  }, []);
  const id = pathId && pathId !== "demo" ? pathId : savedId;
  const targetId = id ?? "dgit-emo";
  const links = [
    ["Command Center", "/", "▦"],
    ["AI Workforce", id ? "/workers" : "/workers?demo=1", "♙"],
    ["Workflow", `/workflows/${targetId}`, "⌘"],
    ["Reports", `/reports/${targetId}`, "▥"],
    ["Marketing", `/marketing/${targetId}`, "⌁"],
    ["Watcher", id ? "/watcher" : "/watcher?demo=1", "⌁"],
    ["Executive Summary", `/executive-summary/${targetId}`, "⌁"],
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
    <main className="appShell">
      <aside className="sidebar">
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
