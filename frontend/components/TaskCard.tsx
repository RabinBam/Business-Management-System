import type { Task } from "@/lib/types";
import { formatNpr } from "@/lib/formatters";
import { ProgressBar } from "./charts/ProgressBar";

export function TaskCard({ task, assignee, progress }: { task: Task; assignee?: string; progress?: number }) {
  return (
    <article className="taskCardNew">
      <div className="taskMeta"><span>{task.priority} priority</span><span>{task.status}</span></div>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <div className="skillList">{task.required_skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
      <dl>
        <div><dt>Role</dt><dd>{task.required_role}</dd></div>
        <div><dt>Difficulty</dt><dd>{task.difficulty}/5</dd></div>
        <div><dt>Experience</dt><dd>{task.minimum_experience_years}+ years</dd></div>
        {assignee && <div><dt>Assigned worker</dt><dd>{assignee}</dd></div>}
        {task.estimated_cost !== undefined && <div><dt>Estimated cost</dt><dd>{formatNpr(task.estimated_cost)}</dd></div>}
        {(task.revision_count ?? 0) > 0 && <div><dt>Revisions</dt><dd>{task.revision_count}</dd></div>}
        <div><dt>Expected output</dt><dd>{task.expected_output}</dd></div>
        <div><dt>Dependencies</dt><dd>{task.dependency_task_ids.length ? task.dependency_task_ids.join(", ") : "None"}</dd></div>
      </dl>
      {task.acceptance_criteria.length > 0 && <div className="criteria"><strong>Acceptance criteria</strong><ul>{task.acceptance_criteria.map((item) => <li key={item}>{item}</li>)}</ul></div>}
      {progress !== undefined && <footer className="taskProgress"><div><strong>Progress</strong><span>{progress}%</span></div><ProgressBar value={progress} tone={progress===100?"green":"blue"}/></footer>}
    </article>
  );
}
