"use client";
import { Line, LineChart, ResponsiveContainer } from "recharts";
export function KpiSparkline({ data }: { data: number[] }) { const values = data.map((value, index) => ({ index, value })); return <div className="sparkline"><ResponsiveContainer width="100%" height="100%"><LineChart data={values}><Line dataKey="value" dot={false} stroke="#6366f1" strokeWidth={3} type="monotone"/></LineChart></ResponsiveContainer></div>; }
