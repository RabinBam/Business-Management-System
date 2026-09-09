import { redirect } from "next/navigation";
import { ExecutiveSummaryView } from "@/components/ExecutiveSummaryView";
export default async function ExecutiveSummaryPage({params}:{params:Promise<{id:string}>}){const{id}=await params;if(id==="demo")redirect("/executive-summary");return <ExecutiveSummaryView id={id}/>}
