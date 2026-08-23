import type { MarketingPlan, Report, Task, WatcherStatus, Workflow } from "./types";

export const demoWorkflow: Workflow = {
  id: "demo", title: "Q3 Product Launch Workflow",
  objective: "Increase Product X sales by 15%, analyze historical performance, optimize spending and prepare a targeted marketing campaign.",
  budget: 500000, deadline: "2026-09-30", status: "EXECUTING", current_stage: "worker_execution", created_at: "2026-08-22T09:30:00+05:45",
};

export const demoTasks: Task[] = [
  { id:"TSK-101",workflow_id:"demo",title:"Historical Sales Analysis",description:"Analyze twelve months of Product X performance and identify revenue, seasonality, and conversion trends.",priority:"HIGH",difficulty:3,required_role:"Sales Analyst",minimum_experience_years:3,required_skills:["Data Analysis","Excel","Sales Analytics"],dependency_task_ids:[],expected_output:"Validated sales performance brief",acceptance_criteria:["Monthly trends quantified","Anomalies documented","Growth baseline approved"],status:"COMPLETED" },
  { id:"TSK-102",workflow_id:"demo",title:"Financial Budget Assessment",description:"Review available campaign funding, operating constraints, and safe allocation thresholds.",priority:"HIGH",difficulty:3,required_role:"Finance Analyst",minimum_experience_years:3,required_skills:["Budgeting","Financial Analysis","Forecasting"],dependency_task_ids:[],expected_output:"Budget assessment and allocation limits",acceptance_criteria:["Total reconciles to approved budget","Risks identified","Contingency retained"],status:"COMPLETED" },
  { id:"TSK-103",workflow_id:"demo",title:"Customer Segment Identification",description:"Identify high-intent customer groups in Kathmandu Valley using approved sales insights.",priority:"HIGH",difficulty:4,required_role:"Marketing Analyst",minimum_experience_years:2,required_skills:["Market Research","Segmentation","Customer Insights"],dependency_task_ids:["TSK-101"],expected_output:"Prioritized audience segments",acceptance_criteria:["Segments are measurable","Channel fit documented","Assumptions stated"],status:"RUNNING" },
  { id:"TSK-104",workflow_id:"demo",title:"Campaign Strategy Development",description:"Create a channel strategy and timeline using approved audience and budget information.",priority:"MEDIUM",difficulty:4,required_role:"Marketing Strategist",minimum_experience_years:4,required_skills:["Campaign Planning","Media Strategy","Copywriting"],dependency_task_ids:["TSK-102","TSK-103"],expected_output:"Editable 30-day campaign plan",acceptance_criteria:["Does not exceed budget","Includes channel rationale","Defines measurable outcomes"],status:"PENDING" },
];

export const demoReport: Report = { workflow_id:"demo",financial:{total_budget:500000,planned_spend:420000,remaining_budget:80000},sales_prediction:{current_sales:1200000,predicted_sales:1380000,growth_percent:15,method:"linear_regression"},risks:["Search advertising costs may rise during the launch window.","Customer-segment assumptions require validation after week one."],recommendations:["Keep NPR 80,000 unallocated as contingency.","Prioritize social and search channels during the first two weeks.","Review conversion performance every five days."] };
export const demoReportChart = [{name:"Current Sales",value:1200000},{name:"Predicted Sales",value:1380000}];

export const demoMarketingPlan: MarketingPlan = { workflow_id:"demo",approved_budget:300000,objective:"Launch a targeted 30-day Product X campaign that converts high-intent customers in Kathmandu Valley.",target_audience:"Urban professionals and university students aged 18–35 in Kathmandu Valley.",allocations:[
  {channel:"Social Media Advertising",amount:120000,reason:"Reach high-intent mobile audiences with measurable conversion campaigns."},
  {channel:"Influencer Partnerships",amount:60000,reason:"Build trust through relevant local creators and product demonstrations."},
  {channel:"Search Advertising",amount:55000,reason:"Capture prospects actively searching for productivity solutions."},
  {channel:"Content Production",amount:40000,reason:"Produce reusable launch videos, landing-page copy, and educational assets."},
  {channel:"Events / Promotions",amount:25000,reason:"Support university and coworking-space product demonstrations."},
],timeline:["Week 1 — Finalize creative assets and tracking","Week 2 — Launch social, search, and influencer activity","Week 3 — Optimize allocation using conversion data","Week 4 — Retarget qualified prospects and compile results"],expected_outcome:"Generate a 15% sales uplift while establishing a repeatable customer-acquisition baseline." };

export const demoWatcherStatus: WatcherStatus = { state:"ACTIVE",active_incidents:1,events:[
  {workflow_id:"demo",component:"Workflow Orchestrator",event_type:"TASK_GENERATION_COMPLETE",message:"Four validated work packages created and dependency-mapped.",retry_count:0,resolved:true,created_at:"2026-08-23T10:42:05+05:45"},
  {workflow_id:"demo",component:"Sales Prediction Service",event_type:"MODEL_EXECUTION_COMPLETE",message:"Linear regression forecast completed with numeric output.",retry_count:0,resolved:true,created_at:"2026-08-23T10:38:12+05:45"},
  {workflow_id:"demo",component:"Marketing Agent",event_type:"RETRY",message:"Structured response validation succeeded after one retry.",retry_count:1,resolved:true,created_at:"2026-08-23T10:15:00+05:45"},
  {workflow_id:"demo",component:"Report Agent",event_type:"VALIDATION_WARNING",message:"One recommendation requires Management review before approval.",retry_count:0,resolved:false,created_at:"2026-08-23T09:55:22+05:45"},
] };

export const demoDashboard = { totalBudget:500000,plannedSpend:420000,remainingBudget:80000,predictedGrowth:15,decisionFeed:[
  {title:"Resource optimization",time:"Just now",message:"Reserved NPR 80,000 as contingency after reviewing projected channel spend."},
  {title:"Audience insight",time:"12 mins ago",message:"Urban professionals and university students show the strongest Product X fit."},
  {title:"Workflow update",time:"34 mins ago",message:"Two tasks completed; customer segmentation is currently running."},
] };

export const demoComponentHealth = [{name:"Workflow Engine",value:"Operational",tone:"healthy"},{name:"Worker Service",value:"4 active tasks",tone:"healthy"},{name:"Report Agent",value:"Review needed",tone:"warning"},{name:"Marketing Agent",value:"Recovered",tone:"healthy"}];

export interface DemoWorker { id:string; name:string; position:string; department:"Sales"|"Finance"|"Marketing"; availability:"AVAILABLE"|"BUSY"|"ON_TASK"|"OFFLINE"; email:string; phone:string; current_assignment:string|null; skills:string[]; experience_level:string; workload:number; initials:string }
export const demoWorkers: DemoWorker[] = [
  {id:"W-101",name:"Aarav Sharma",position:"Senior Sales Analyst",department:"Sales",availability:"ON_TASK",email:"aarav@kathmandudigital.com",phone:"+977-9812345678",current_assignment:"Q3 Revenue Projection Model",skills:["Sales Analytics","Forecasting","Excel"],experience_level:"Level 4 Expert",workload:78,initials:"AS"},
  {id:"W-102",name:"Maya Karki",position:"Finance Auditor",department:"Finance",availability:"AVAILABLE",email:"maya@kathmandudigital.com",phone:"+977-9823456789",current_assignment:null,skills:["Budgeting","Audit","Financial Analysis"],experience_level:"Level 3 Senior",workload:20,initials:"MK"},
  {id:"W-103",name:"Saanvi Thapa",position:"Brand Copywriter",department:"Marketing",availability:"BUSY",email:"saanvi@kathmandudigital.com",phone:"+977-9834567890",current_assignment:"Product Launch Campaign Copy",skills:["Copywriting","Brand Strategy","Content"],experience_level:"Level 5 Master",workload:64,initials:"ST"},
  {id:"W-104",name:"Rohan Gurung",position:"Market Research Analyst",department:"Marketing",availability:"AVAILABLE",email:"rohan@kathmandudigital.com",phone:"+977-9845678901",current_assignment:null,skills:["Research","Segmentation","Survey Design"],experience_level:"Level 2 Specialist",workload:15,initials:"RG"},
  {id:"W-105",name:"Ishani Rai",position:"Revenue Operations Lead",department:"Sales",availability:"OFFLINE",email:"ishani@kathmandudigital.com",phone:"+977-9856789012",current_assignment:"Sales Process Audit",skills:["CRM","Revenue Ops","Planning"],experience_level:"Level 4 Expert",workload:45,initials:"IR"},
  {id:"W-106",name:"Nirav Joshi",position:"Financial Planning Analyst",department:"Finance",availability:"ON_TASK",email:"nirav@kathmandudigital.com",phone:"+977-9867890123",current_assignment:"Campaign Budget Assessment",skills:["FP&A","Forecasting","Risk"],experience_level:"Level 3 Senior",workload:82,initials:"NJ"},
];
export const demoCompanyMetrics={totalBudget:4200000,estimatedSpend:1800000,predictedGrowth:24.5,budgetTrend:[1.8,2.1,2.6,3.1,3.6,4.2],growthHistory:[8,11,9,15,13,19,16,22,18,24.5],confidence:92};
export const demoCategoryBreakdown=[{name:"Operations",value:40},{name:"Marketing",value:25},{name:"R&D",value:20},{name:"Other",value:15}];
export const demoSalesForecast=[{month:"Jan",historical:80},{month:"Feb",historical:86},{month:"Mar",historical:91},{month:"Apr",historical:94},{month:"May",forecast:101},{month:"Jun",forecast:109},{month:"Jul",forecast:114}];
export const demoTaskProgress:Record<string,number>={"TSK-101":100,"TSK-102":100,"TSK-103":65,"TSK-104":0};
export const demoTaskAssignees:Record<string,string>={"TSK-101":"Aarav Sharma","TSK-102":"Maya Karki","TSK-103":"Rohan Gurung","TSK-104":"Saanvi Thapa"};
export const demoExecutiveSummary={activeWorkflows:3,completedWorkflows:12,totalRevenue:4200000,marketingRoi:245,decisionAccuracy:98.2,salesGrowth:15,marketingStatus:"Plan awaiting approval",recommendations:["Approve the Product X channel allocation.","Retain NPR 80,000 campaign contingency.","Review the open Report Agent validation warning."],workflowCompletion:[{name:"Product X Launch",value:62},{name:"Customer Retention",value:84},{name:"Finance Automation",value:100}]};
