"use client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { FinancialDataRow } from "@/lib/financialParser";
const compact = (value:number) => new Intl.NumberFormat("en", { notation:"compact", maximumFractionDigits:1 }).format(value);
export function BudgetExpenseChart({ rows }:{ rows:FinancialDataRow[] }) { return <div className="dataChart"><ResponsiveContainer width="100%" height="100%"><BarChart data={rows} margin={{top:10,right:12,left:2,bottom:4}}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="period" tick={{fontSize:11}}/><YAxis domain={[0,"auto"]} tickFormatter={compact} tick={{fontSize:11}}/><Tooltip formatter={(value,name)=>[`NPR ${Number(value).toLocaleString()}`,name]}/><Legend/><Bar dataKey="totalBudget" name="Budget" fill="#b8b6f7" radius={[4,4,0,0]}/><Bar dataKey="expense" name="Expense" fill="#131b2e" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div> }
