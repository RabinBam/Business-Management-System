import Link from "next/link";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="centeredState">
      <span className="brandMark">AF</span>
      <p className="eyebrow">Workflow {id}</p>
      <h1>Report surface ready</h1>
      <p>Person 2 owns the data contract. Person 5 owns this financial and sales-prediction view.</p>
      <Link className="buttonLink" href={`/workflows/${id}`}>Back to workflow</Link>
    </main>
  );
}

