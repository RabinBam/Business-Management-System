"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createWorkflow, runWorkflow } from "@/lib/api";
import { formatDate, formatNpr } from "@/lib/formatters";
import type { Workflow } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";

export function ExecutiveObjectiveForm({ onCreated }: { onCreated?: () => void }) {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    objective: "",
    budget: "",
    deadline: "",
    execution_mode: "employee",
    sales_history: "",
  });
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [pending, setPending] = useState<"create" | "run" | null>(null);
  const [error, setError] = useState("");
  const change = (key: keyof typeof form, value: string) =>
    setForm((current) => ({ ...current, [key]: value }));

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (pending) return;
    setPending("create");
    setError("");
    try {
      const months = form.sales_history.trim() ? form.sales_history.split(",").map(v => v.trim()) : [];
      if (months.some(v => !v || !Number.isFinite(Number(v)) || Number(v) < 0)) {
        throw new Error("Enter non-negative monthly revenue amounts separated by commas.");
      }
      const created = await createWorkflow({
        ...form,
        budget: Number(form.budget),
        execution_mode: form.execution_mode as "ai" | "employee",
        sales_history: months.map(Number),
      });
      setWorkflow(created);
      onCreated?.();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to create workflow.",
      );
    } finally {
      setPending(null);
    }
  }
  async function run() {
    if (!workflow || pending) return;
    setPending("run");
    setError("");
    try {
      const updated = await runWorkflow(workflow.id);
      setWorkflow(updated);
      router.push(`/workflows/${updated.id}`);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unable to run workflow.",
      );
      setPending(null);
    }
  }

  return (
    <div className="objectiveStack">
      <form className="objectiveFormNew" onSubmit={submit}>
        <header>
          <div>
            <h2>Executive Objective Formulation</h2>
            <p>
              Define high-level business goals to initialize an automated
              workflow.
            </p>
          </div>
          <span>⚑</span>
        </header>
        <label>
          Workflow title
          <input
            required
            minLength={3}
            maxLength={120}
            value={form.title}
            onChange={(event) => change("title", event.target.value)}
            placeholder="Product X Growth Campaign"
          />
        </label>
        <label>
          Business objective
          <textarea
            required
            minLength={10}
            maxLength={2000}
            rows={5}
            value={form.objective}
            onChange={(event) => change("objective", event.target.value)}
            placeholder="Increase Product X sales by 15%, analyze historical performance and prepare a marketing plan."
          />
        </label>
        <div className="formColumns">
          <label>
            Budget (NPR)
            <input
              required
              min="0"
              type="number"
              value={form.budget}
              onChange={(event) => change("budget", event.target.value)}
              placeholder="500000"
            />
          </label>
          <label>
            Deadline
            <input
              required
              type="date"
              value={form.deadline}
              onChange={(event) => change("deadline", event.target.value)}
            />
          </label>
        </div>
        <label>Who completes the tasks?
          <select value={form.execution_mode} onChange={e => change("execution_mode", e.target.value)}>
            <option value="employee">Employees submit work; AI reviews it</option>
            <option value="ai">AI generates written deliverables</option>
          </select>
        </label>
        <label>Monthly revenue history (optional)
          <input value={form.sales_history} onChange={e => change("sales_history", e.target.value)} placeholder="Your consecutive monthly amounts, oldest first, separated by commas" />
        </label>
        <p>No forecast is shown without at least two monthly revenue values. The budget is a planning limit, not a payment.</p>
        {error && (
          <p className="inlineError" role="alert">
            {error}
          </p>
        )}
        <footer>
          <button
            disabled={Boolean(pending) || Boolean(workflow)}
            type="submit"
          >
            {pending === "create"
              ? "Creating…"
              : workflow
                ? "Workflow Created"
                : "Create Workflow"}
          </button>
        </footer>
      </form>
      {workflow && (
        <section className="createdWorkflow" aria-live="polite">
          <header>
            <div>
              <span>Workflow created successfully</span>
              <h2>{workflow.title}</h2>
            </div>
            <StatusBadge status={workflow.status} />
          </header>
          <dl>
            <div>
              <dt>Budget</dt>
              <dd>{formatNpr(workflow.budget)}</dd>
            </div>
            <div>
              <dt>Deadline</dt>
              <dd>{formatDate(workflow.deadline)}</dd>
            </div>
            <div>
              <dt>Current stage</dt>
              <dd>{workflow.current_stage.replaceAll("_", " ")}</dd>
            </div>
          </dl>
          <button onClick={run} disabled={Boolean(pending)}>
            {pending === "run" ? "Starting…" : "Run Workflow →"}
          </button>
        </section>
      )}
    </div>
  );
}
