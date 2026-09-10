"use client";
import { useState } from "react";
import { request } from "@/lib/api";
export function DemoResetButton() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function reset() {
    if (busy) return;
    setBusy(true); setError("");
    try { await request("/employees/demo/reset", { method: "POST" }); window.location.assign("/"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Reset failed"); setBusy(false); }
  }
  return <section className="workspaceNotice"><button className="secondaryButton" disabled={busy} onClick={() => void reset()}>{busy ? "Resetting…" : "Reset demo data"}</button><p>Backs up and clears workflows, tasks, reports, marketing, events and money. Keeps employees and API settings.</p>{error && <p role="alert">{error}</p>}</section>;
}
