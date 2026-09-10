"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppShell } from "./AppShell";
import { EmptyState, ErrorState, LoadingSkeleton } from "./AsyncStates";
import { ApiError, getMarketingPlan, updateMarketingPlan, request, getWorkflow } from "@/lib/api";
import { formatNpr } from "@/lib/formatters";
import type { MarketingPlan } from "@/lib/types";
import { demoMarketingPlan } from "@/lib/demoData";

export function MarketingView({ id }: { id: string }) {
  const router = useRouter();
  const [approved, setApproved] = useState(false);
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
    setError("");
    try {
      setPlan(await getMarketingPlan(id));
      const workflow = await getWorkflow(id);
      setApproved(["FINAL_REVIEW", "COMPLETED"].includes(workflow.status));
      setError("");
    } catch (reason) {
      if (reason instanceof ApiError && reason.code === "MARKETING_NOT_READY") { setPlan(null); return; }
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
      setMessage("Marketing draft saved. Confirm it when the team is ready.");
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
  async function approve() {
    if (!plan || saving || exceeded || approved) return;
    setSaving(true); setError("");
    try {
      await request(`/workflows/${id}/marketing/approve`, { method: "POST", body: JSON.stringify(plan) });
      setApproved(true);
      router.push(`/workflows/${id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to approve marketing.");
    } finally { setSaving(false); }
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
          title="Marketing is waiting for the workflow"
          message="Complete task review and run the workflow through reporting and marketing. If the AI request failed, retry from the workflow page."
        />
        <Link className="primaryButton" href={`/workflows/${id}`}>Open workflow</Link>
        <button className="secondaryButton" onClick={() => void load()}>Check again</button>
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
          disabled={saving || exceeded || approved}
          onClick={save}
        >
          {saving
            ? "Saving…"
            : isDemo
              ? "Save Demo Changes"
              : "Save Marketing Plan"}
        </button>
      </header>
      <section className="workspaceNotice"><strong>{approved ? "Marketing confirmed" : "Waiting for marketing confirmation"}</strong><p>{approved ? "This plan is confirmed. Continue the workflow to complete final review." : "Edit the plan below. Save keeps it as a draft. Confirm saves your current edits and releases the workflow to final review."}</p>{!approved && <button className="primaryButton" disabled={saving || exceeded} onClick={() => void approve()}>Confirm marketing & proceed to final review</button>}<p><Link href={`/workflows/${id}`}>Open workflow →</Link></p></section>
      <section className="workspaceNotice"><strong>Marketing team handoff</strong><p>This campaign builds on the reviewed employee work and finance budget. Refine the audience, outcome, schedule and allocations, then save. Saving records a plan; it does not launch advertisements.</p><div className="contextLinks"><Link href="/tasks">Team briefings & assignments →</Link><Link href={`/executive-summary/${id}`}>CEO summary →</Link></div></section>
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
        <aside className="planDetails workspaceCard">
          <section>
            <span>Target audience</span>
            <textarea aria-label="Target audience" rows={3} value={plan.target_audience} onChange={e => setPlan({...plan,target_audience:e.target.value})}/>
          </section>
          <section>
            <span>Expected outcome</span>
            <textarea aria-label="Expected outcome" rows={4} value={plan.expected_outcome} onChange={e => setPlan({...plan,expected_outcome:e.target.value})}/>
          </section>
          <section className="timelineSection">
            <span>Execution Timeline</span>
            <textarea aria-label="Execution timeline, one step per line" rows={7} value={plan.timeline.join("\n")} onChange={e => setPlan({...plan,timeline:e.target.value.split("\n")})}/>
          </section>
        </aside>
      </div>
    </AppShell>
  );
}
