"use client";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
export interface ForecastPoint { month:string; historical?:number; forecast?:number }
export function ForecastChart({ data }: { data: ForecastPoint[] }) { return <div className="forecastChart"><ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid vertical={false} strokeDasharray="3 3"/><XAxis dataKey="month"/><YAxis/><Tooltip/><Legend/><Bar dataKey="historical" fill="#111827" radius={[5,5,0,0]}/><Bar dataKey="forecast" fill="#a5b4fc" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div>; }
