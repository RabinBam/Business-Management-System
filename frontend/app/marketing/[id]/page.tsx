import Link from "next/link";

export default async function MarketingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="centeredState">
      <span className="brandMark">AF</span>
      <p className="eyebrow">Workflow {id}</p>
      <h1>Marketing workspace ready</h1>
      <p>Person 3 owns validated plan data. Person 5 owns the human budget editor on this route.</p>
      <Link className="buttonLink" href={`/workflows/${id}`}>Back to workflow</Link>
    </main>
  );
}

