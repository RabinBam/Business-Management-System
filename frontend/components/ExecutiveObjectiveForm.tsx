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
          <p className="panelLabel">New directive</p>
          <h2>Set the executive objective</h2>
        </div>
        <span className="liveChip"><i /> Ready</span>
      </div>

      <label>
        Initiative name
        <input name="title" required minLength={3} maxLength={120} defaultValue="Regional product launch" />
      </label>

      <label>
        Objective
        <textarea
          name="objective"
          required
          minLength={10}
          maxLength={2000}
          rows={5}
          defaultValue="Launch the new service in Kathmandu with a measurable sales plan, controlled marketing budget, and clear management reporting."
        />
      </label>

      <div className="formRow">
        <label>
          Approved budget
          <div className="inputPrefix"><span>NPR</span><input name="budget" type="number" min="0" step="1000" defaultValue="500000" required /></div>
        </label>
        <label>
          Deadline
          <input name="deadline" type="date" defaultValue={defaultDeadline()} required />
        </label>
      </div>

      {error && <p className="formError" role="alert">{error}</p>}
      <button type="submit" disabled={pending}>
        {pending ? "Starting workflow…" : "Execute workflow"}
        <span aria-hidden="true">→</span>
      </button>
    </form>
  );
}

