import { AppShell } from "@/components/AppShell";
import { ExecutiveObjectiveForm } from "@/components/ExecutiveObjectiveForm";

const stages = ["Executive Goal", "Segmentation", "Assignment", "Execution", "Review", "Reporting", "Marketing", "Final Review"];
export default function HomePage() {
  return <AppShell><header className="pageTitle"><div><span>Executive workspace</span><h1>Command Center</h1><p>Turn a business objective into visible, accountable work.</p></div></header><div className="commandColumns"><section><ExecutiveObjectiveForm/><div className="overviewCard"><header><h2>Workflow Overview</h2><p>The live workflow page highlights each stage using the state returned by FastAPI.</p></header><ol>{stages.map((stage, index) => <li key={stage}><i>{index + 1}</i><span>{stage}</span></li>)}</ol></div></section><aside className="principlesCard"><span>Byapari operating model</span><h2>Human authority stays visible.</h2><p>Management controls approvals and information boundaries while AI modules plan, delegate, analyze, and report.</p><ul><li>Role-aware delegation</li><li>Backend-validated decisions</li><li>Human-edited marketing plans</li><li>Watcher failure recovery</li></ul></aside></div></AppShell>;
}
