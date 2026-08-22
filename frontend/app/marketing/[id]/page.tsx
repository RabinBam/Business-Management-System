import { MarketingView } from "@/components/MarketingView";
export default async function MarketingPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <MarketingView id={id}/>; }
