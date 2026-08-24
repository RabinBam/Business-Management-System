"use client";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { FinancialDataRow } from "@/lib/financialParser";
export function SalesUnitsChart({ rows }:{ rows:FinancialDataRow[] }) { return <div className="dataChart small"><ResponsiveContainer width="100%" height="100%"><AreaChart data={rows} margin={{top:8,right:10,left:0,bottom:3}}><XAxis dataKey="period" tick={{fontSize:10}}/><YAxis domain={[0,"auto"]} tick={{fontSize:10}}/><Tooltip formatter={(value)=>[Number(value).toLocaleString(),"Sales units"]}/><Area dataKey="salesUnits" name="Sales units" type="monotone" stroke="#10b981" fill="#d9f7ec" strokeWidth={2}/></AreaChart></ResponsiveContainer></div> }
