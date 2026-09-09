import { redirect } from "next/navigation";
import { ReportView } from "@/components/ReportView";
export default async function ReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  if (id === "demo") redirect("/reports");
  return <ReportView id={id} />;
}
