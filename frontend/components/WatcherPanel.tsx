"use client";

import { useEffect, useState } from "react";

import { getWatcherStatus } from "@/lib/api";
import type { WatcherStatus } from "@/lib/types";

export function WatcherPanel() {
  const [watcher, setWatcher] = useState<WatcherStatus | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getWatcherStatus().then(setWatcher).catch((reason) => setError(reason instanceof Error ? reason.message : "Watcher unavailable"));
  }, []);

  if (error) return <div className="emptyState"><strong>Watcher unavailable</strong><p>{error}</p></div>;
  if (!watcher) return <div className="emptyState"><strong>Loading activity…</strong></div>;

  return (
    <section className="watcherPanel">
      <div className="watcherSummary">
        <span className={`watcherOrb ${watcher.state.toLowerCase()}`} />
        <div><span>System state</span><strong>{watcher.state}</strong></div>
        <div><span>Active incidents</span><strong>{watcher.active_incidents}</strong></div>
      </div>
      {watcher.events.length ? (
        <ol className="eventList">
          {watcher.events.map((event, index) => (
            <li key={`${event.created_at}-${index}`}>
              <time>{new Date(event.created_at).toLocaleTimeString()}</time>
              <strong>{event.component}</strong>
              <span>{event.event_type}</span>
              <p>{event.message}</p>
            </li>
          ))}
        </ol>
      ) : (
        <div className="emptyState"><strong>No incidents recorded.</strong><p>The watcher is idle and ready to record retry or recovery events.</p></div>
      )}
    </section>
  );
}

