"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { getWorkers } from "@/lib/api";
import type { Worker } from "@/lib/types";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { ProgressBar } from "./charts/ProgressBar";

function initials(name: string) {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function WorkersView() {
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [filter, setFilter] = useState("All");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setWorkers(await getWorkers());
      setError("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to load workers.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [load]);

  const filters = useMemo(
    () => ["All", "Available", ...new Set(workers.map((worker) => worker.department))],
    [workers],
  );
  const visible = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return workers.filter((worker) => {
      const filterMatches =
        filter === "All" ||
        (filter === "Available"
          ? worker.availability === "AVAILABLE"
          : worker.department === filter);
      const queryMatches =
        !normalizedQuery ||
        `${worker.name} ${worker.role} ${worker.department} ${worker.skills.join(" ")}`
          .toLowerCase()
          .includes(normalizedQuery);
      return filterMatches && queryMatches;
    });
  }, [filter, query, workers]);

  return (
    <>
      <header className="pageTitle">
        <div>
          <span>Company resources</span>
          <h1>AI Workforce</h1>
          <p>Live matching capacity, skills, availability, and workflow workload.</p>
        </div>
        <span className="directoryBadge">{workers.length} workers</span>
      </header>
      <section className="workerToolbar">
        <div>
          {filters.map((item) => (
            <button
              className={filter === item ? "active" : ""}
              key={item}
              onClick={() => setFilter(item)}
            >
              {item}
            </button>
          ))}
        </div>
        <input
          aria-label="Search workers"
          placeholder="Search name, role, department or skill"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </section>
      {loading ? (
        <LoadingSkeleton rows={4} />
      ) : error ? (
        <ErrorState message={error} retry={() => void load()} />
      ) : visible.length === 0 ? (
        <EmptyState
          title="No matching workers"
          message="Try another department, availability, or search term."
        />
      ) : (
        <section className="workerBento">
          {visible.map((worker) => (
            <article className="workerCard" key={worker.id}>
              <header>
                <span className="workerAvatar">{initials(worker.name)}</span>
                <div>
                  <h2>{worker.name}</h2>
                  <p>{worker.role}</p>
                </div>
                <small className={worker.availability.toLowerCase()}>
                  {worker.availability.replaceAll("_", " ")}
                </small>
              </header>
              <div className="workerMeta">
                <span>{worker.department}</span>
                <b>{worker.experience_years} years</b>
              </div>
              <dl>
                <div><dt>Worker ID</dt><dd>{worker.id}</dd></div>
                <div><dt>Active tasks</dt><dd>{worker.active_tasks}</dd></div>
                <div><dt>Capacity</dt><dd>{100 - worker.workload_percent}% available</dd></div>
              </dl>
              <div className="workerSkills">
                {worker.skills.map((skill) => <span key={skill}>{skill}</span>)}
              </div>
              <footer>
                <div><b>Workload</b><strong>{worker.workload_percent}%</strong></div>
                <ProgressBar value={worker.workload_percent} />
              </footer>
            </article>
          ))}
        </section>
      )}
    </>
  );
}
