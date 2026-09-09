import { redirect } from "next/navigation";
import { WorkflowView } from "@/components/WorkflowView";
export default async function WorkflowPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  if (id === "demo") redirect("/workflows");
  return <WorkflowView id={id} />;
}
