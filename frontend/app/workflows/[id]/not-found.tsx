import Link from "next/link";

export default function WorkflowNotFound() {
  return (
    <main className="centeredState">
      <span className="brandMark">AF</span>
      <h1>Workflow not available</h1>
      <p>It may have been cleared when the development backend restarted.</p>
      <Link className="buttonLink" href="/">Create a new workflow</Link>
    </main>
  );
}

