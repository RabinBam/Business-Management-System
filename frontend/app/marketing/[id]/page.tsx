import { redirect } from "next/navigation";
import { MarketingView } from "@/components/MarketingView";

export default async function MarketingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  if (id === "demo") redirect("/marketing");
  return <MarketingView id={id} />;
}
