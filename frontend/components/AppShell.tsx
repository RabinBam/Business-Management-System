"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { SidebarLayout } from "./SidebarLayout";

function activeSection(pathname: string) {
  if (pathname === "/") return "command";
  if (pathname.startsWith("/workers")) return "workers";
  if (pathname.startsWith("/workflows")) return "workflow";
  if (pathname.startsWith("/reports")) return "reports";
  if (pathname.startsWith("/marketing")) return "marketing";
  if (pathname.startsWith("/watcher")) return "watcher";
  return "executive";
}

export function AppShell({
  children,
}: {
  children: ReactNode;
  mode?: "demo" | "real";
}) {
  const pathname = usePathname();
  return <SidebarLayout active={activeSection(pathname)}>{children}</SidebarLayout>;
}
