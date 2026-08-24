<<<<<<< HEAD
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

=======
import Link from "next/link";

export default function WorkflowNotFound() {
  return (
    <main className="centeredState">
      <span className="brandMark">AF</span>
      <h1>Workflow not available</h1>
      <p>It may have been cleared when the development backend restarted.</p>
      <Link className="buttonLink" href="/">
        Create a new workflow
      </Link>
    </main>
  );
}
>>>>>>> 3ffc1b091eeeb5d0c2ea50affbb8c90e7a14e16e
