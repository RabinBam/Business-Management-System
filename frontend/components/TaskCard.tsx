import type { Task } from "@/lib/types";

export function TaskCard({ task }: { task: Task }) {
  return (
    <article className="taskCard">
      <div className="taskMeta"><span>{task.priority}</span><span>{task.status}</span></div>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
      <div className="skillList">{task.required_skills.map((skill) => <span key={skill}>{skill}</span>)}</div>
      <dl>
        <div><dt>Role</dt><dd>{task.required_role}</dd></div>
        <div><dt>Difficulty</dt><dd>{task.difficulty}/5</dd></div>
        <div><dt>Experience</dt><dd>{task.minimum_experience_years}+ years</dd></div>
      </dl>
    </article>
  );
}

