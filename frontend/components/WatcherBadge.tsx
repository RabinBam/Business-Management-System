"use client";

import { useEffect, useState } from "react";

import { getWatcherStatus } from "@/lib/api";
import type { WatcherState } from "@/lib/types";

export function WatcherBadge() {
  const [state, setState] = useState<WatcherState>("IDLE");

  useEffect(() => {
    getWatcherStatus().then((watcher) => setState(watcher.state)).catch(() => setState("ACTIVE"));
  }, []);

  return <span className={`watcherBadge ${state.toLowerCase()}`}><i /> Watcher: {state}</span>;
}

