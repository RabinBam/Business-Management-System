<<<<<<< HEAD
"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { createWorkflow, runWorkflow } from "@/lib/api";

function defaultDeadline() {
  const value = new Date();
  value.setDate(value.getDate() + 30);
  return value.toISOString().slice(0, 10);
}

export function ExecutiveObjectiveForm() {
  const router = useRouter();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError("");
    const form = new FormData(event.currentTarget);

    try {
      const workflow = await createWorkflow({
        title: String(form.get("title")),
        objective: String(form.get("objective")),
        budget: Number(form.get("budget")),
        deadline: String(form.get("deadline")),
      });
      await runWorkflow(workflow.id);
      router.push(`/workflows/${workflow.id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to start the workflow.");
      setPending(false);
    }
  }

  return (
    <form className="objectiveForm" onSubmit={submit}>
      <div className="formHeading">
        <div>
          <h2>Executive Objective Formulation</h2>
          <p>Define high-level business goals to initialize automated workflows.</p>
        </div>
        <span className="formFlag" aria-hidden="true">⚑</span>
      </div>

      <input name="title" type="hidden" value="Executive business objective" readOnly />
      <label>
        Primary Directive
        <textarea
          name="objective"
          required
          minLength={10}
          maxLength={2000}
          rows={5}
          placeholder="Enter Q3 operational targets..."
        />
      </label>

      <div className="formRow">
        <label>
          Target Completion
          <input name="deadline" type="date" defaultValue={defaultDeadline()} required />
        </label>
        <label>
          Budget Allocation (NPR)
          <div className="inputPrefix"><span>रु</span><input name="budget" type="number" min="0" step="1000" placeholder="0.00" required /></div>
        </label>
      </div>

      {error && <p className="formError" role="alert">{error}</p>}
      <div className="formActions">
        <button type="button" className="draftButton">Save Draft</button>
        <button type="submit" disabled={pending}>{pending ? "Deploying…" : "Deploy Objective"}</button>
      </div>
    </form>
  );
}

=======
"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { createWorkflow, runWorkflow } from "@/lib/api";
import { formatDate, formatNpr } from "@/lib/formatters";
import type { Workflow } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";

function defaultDeadline() {
  const date = new Date();
  date.setDate(date.getDate() + 30);
  return date.toISOString().slice(0, 10);
}

export function ExecutiveObjectiveForm() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    objective: "",
    budget: "",
    deadline: defaultDeadline(),
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
      const created = await createWorkflow({
        ...form,
        budget: Number(form.budget),
      });
      setWorkflow(created);
      window.localStorage.setItem("byapari:lastWorkflowId", created.id);
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
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
