import { ExecutiveSummaryView } from "@/components/ExecutiveSummaryView";
export default async function ExecutiveSummaryPage({params}:{params:Promise<{id:string}>}){const{id}=await params;return <ExecutiveSummaryView id={id}/>}
