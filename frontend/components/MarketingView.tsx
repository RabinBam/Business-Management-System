"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { getMarketingPlan, updateMarketingPlan } from "@/lib/api";
import { formatNpr } from "@/lib/formatters";
import type { MarketingPlan } from "@/lib/types";
import { demoMarketingPlan } from "@/lib/demoData";

export function MarketingView({ id }: { id: string }) {
  const isDemo = id === "demo";
  const [plan, setPlan] = useState<MarketingPlan | null>(
    isDemo ? demoMarketingPlan : null,
  );
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(!isDemo);
  const [saving, setSaving] = useState(false);
  const load = useCallback(async () => {
    setLoading(true);
    try {
      setPlan(await getMarketingPlan(id));
      setError("");
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to load marketing plan.",
      );
    } finally {
      setLoading(false);
    }
  }, [id]);
  useEffect(() => {
    if (isDemo) return;
    const timer = window.setTimeout(() => void load(), 0);
    return () => window.clearTimeout(timer);
  }, [isDemo, load]);
  const allocated = useMemo(
    () => plan?.allocations.reduce((sum, item) => sum + item.amount, 0) ?? 0,
    [plan],
  );
  const exceeded = Boolean(plan && allocated > plan.approved_budget);
  function updateAmount(index: number, amount: number) {
    setPlan((current) =>
      current
        ? {
            ...current,
            allocations: current.allocations.map((item, itemIndex) =>
              itemIndex === index
                ? { ...item, amount: Math.max(0, amount) }
                : item,
            ),
          }
        : current,
    );
    setMessage("");
  }
  async function save() {
    if (!plan || exceeded || saving) return;
    setSaving(true);
    setError("");
    setMessage("");
    if (isDemo) {
      setMessage("Demo changes saved locally.");
      setSaving(false);
      return;
    }
    try {
      setPlan(await updateMarketingPlan(id, plan));
      setMessage("Marketing plan saved and validated by the backend.");
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Unable to save marketing plan.",
      );
    } finally {
      setSaving(false);
    }
  }
  if (loading)
    return (
      <AppShell>
        <LoadingSkeleton rows={5} />
      </AppShell>
    );
  if (error && !plan)
    return (
      <AppShell>
        <ErrorState message={error} retry={() => void load()} />
        <p className="availabilityHint">
          Marketing recommendations appear after the reporting stage is
          complete.
        </p>
      </AppShell>
    );
  if (!plan)
    return (
      <AppShell>
        <EmptyState
          title="No marketing plan"
          message="Marketing recommendations will appear after the reporting stage is complete."
        />
      </AppShell>
    );
  return (
    <AppShell mode={isDemo ? "demo" : "real"}>
      <header className="pageTitle">
        <div>
          <span>Human-in-the-loop planning</span>
          <h1>Campaign Planner</h1>
          <p>{plan.objective}</p>
        </div>
        <button
          className="primaryButton"
          disabled={saving || exceeded}
          onClick={save}
        >
          {saving
            ? "Saving…"
            : isDemo
              ? "Save Demo Changes"
              : "Save Marketing Plan"}
        </button>
      </header>
      {error && (
        <p className="inlineError" role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className="successMessage" role="status">
          {message}
        </p>
      )}
      <div className="marketingGrid">
        <section className="budgetEditor">
          <header>
            <div>
              <span>Budget Allocation</span>
              <h2>
                {formatNpr(allocated)}{" "}
                <small>used of {formatNpr(plan.approved_budget)}</small>
              </h2>
            </div>
            <strong className={exceeded ? "over" : ""}>
              {plan.approved_budget
                ? Math.round((allocated / plan.approved_budget) * 100)
                : 0}
              %
            </strong>
          </header>
          <div className="budgetProgress">
            <i
              className={exceeded ? "over" : ""}
              style={{
                width: `${Math.min(plan.approved_budget ? (allocated / plan.approved_budget) * 100 : 0, 100)}%`,
              }}
            />
          </div>
          {exceeded && (
            <p className="budgetWarning">
              Allocation exceeds the approved budget by{" "}
              {formatNpr(allocated - plan.approved_budget)}. Reduce an amount
              before saving.
            </p>
          )}
          <div className="allocationList">
            {plan.allocations.map((item, index) => (
              <article key={`${item.channel}-${index}`}>
                <span className="channelIcon">{index + 1}</span>
                <div>
                  <label htmlFor={`allocation-${index}`}>{item.channel}</label>
                  <p>{item.reason}</p>
                </div>
                <input
                  aria-label={`${item.channel} allocation`}
                  id={`allocation-${index}`}
                  min="0"
                  type="number"
                  value={item.amount}
                  onChange={(event) =>
                    updateAmount(index, Number(event.target.value))
                  }
                />
              </article>
            ))}
          </div>
        </section>
        <aside className="planDetails">
          <section>
            <span>Target audience</span>
            <p>{plan.target_audience}</p>
          </section>
          <section>
            <span>Expected outcome</span>
            <p>
              {plan.expected_outcome || "No expected outcome was returned."}
            </p>
          </section>
          <section className="timelineSection">
            <span>Execution Timeline</span>
            {plan.timeline.length ? (
              <ol>
                {plan.timeline.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            ) : (
              <p>No timeline was returned.</p>
            )}
          </section>
        </aside>
      </div>
    </AppShell>
  );
}
