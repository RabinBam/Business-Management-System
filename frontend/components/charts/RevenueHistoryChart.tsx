"use client";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { FinancialDataRow } from "@/lib/financialParser";
const compact = (value:number) => new Intl.NumberFormat("en", { notation:"compact", maximumFractionDigits:1 }).format(value);
export function RevenueHistoryChart({ rows }:{ rows:FinancialDataRow[] }) { return <div className="dataChart"><ResponsiveContainer width="100%" height="100%"><LineChart data={rows} margin={{top:10,right:12,left:2,bottom:4}}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="period" tick={{fontSize:11}}/><YAxis domain={[0,"auto"]} tickFormatter={compact} tick={{fontSize:11}}/><Tooltip formatter={(value)=>[`NPR ${Number(value).toLocaleString()}`,"Revenue"]}/><Line dataKey="revenue" name="Revenue" type="monotone" stroke="#6366f1" strokeWidth={3} dot={{r:4}}/></LineChart></ResponsiveContainer></div> }
