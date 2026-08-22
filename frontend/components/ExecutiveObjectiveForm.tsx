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

