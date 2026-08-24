"use client";
import { useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { splitFinancialRows, type FinancialDataRow } from "@/lib/financialParser";
import { formatNpr } from "@/lib/formatters";
import { BudgetExpenseChart } from "../charts/BudgetExpenseChart";
import { SalesUnitsChart } from "../charts/SalesUnitsChart";
import styles from "./ReportAnalytics.module.css";

const compact = (value:number) => new Intl.NumberFormat("en",{notation:"compact",maximumFractionDigits:1}).format(value);
const moneyTooltip = (value:unknown) => formatNpr(Number(Array.isArray(value) ? value[0] : value ?? 0));
const tooltipStyle = { border:"1px solid #e2e8f0", borderRadius:10, fontSize:12 };
const monthName = (month?:number) => month ? new Date(2026,month-1,1).toLocaleString("en",{month:"short"}) : "";
const EmptyChart = ({message}:{message:string}) => <div className={styles.empty}>{message}</div>;

export function ReportAnalytics({ rows }: { rows: FinancialDataRow[] }) {
  const { yearly, monthly } = useMemo(() => splitFinancialRows(rows), [rows]);
  const years = useMemo(() => [...new Set(monthly.map(row => row.year).filter((year):year is number => Boolean(year)))].sort((a,b)=>b-a), [monthly]);
  const [requestedYear,setRequestedYear] = useState<number|undefined>();
  const selectedYear = requestedYear && years.includes(requestedYear) ? requestedYear : years[0];
  const selectedMonthly = monthly.filter(row => row.year === selectedYear);
  const latest = yearly.at(-1) ?? selectedMonthly.at(-1) ?? rows.at(-1);
  const previous = yearly.length > 1 ? yearly.at(-2) : undefined;
  const growth = latest?.revenueGrowthPercent ?? (latest && previous && previous.revenue ? (latest.revenue-previous.revenue)/previous.revenue*100 : undefined);
  const yearlyData = yearly.map(row => ({...row,label:String(row.year ?? row.period),grossProfit:row.grossProfit ?? row.revenue-row.expense}));
  const monthlyData = selectedMonthly.map(row => ({...row,label:monthName(row.month),grossProfit:row.grossProfit ?? row.revenue-row.expense}));
  const growthData = yearlyData.map((row,index) => ({
    ...row,
    growth: row.revenueGrowthPercent ?? (index > 0 ? (row.revenue - yearlyData[index - 1].revenue) / yearlyData[index - 1].revenue * 100 : null),
  }));
  const chartRows = monthlyData.length ? selectedMonthly : yearly;
  const highest = yearly.reduce<FinancialDataRow|undefined>((best,row) => !best || row.revenue > best.revenue ? row : best, undefined);
  const annualAverage = yearly.length ? yearly.reduce((sum,row)=>sum+row.revenue,0)/yearly.length : 0;
  return <section className={styles.analytics} aria-label="Financial analytics">
    {latest && <div className={styles.summary}>
      <article><span>Total revenue</span><strong>{formatNpr(latest.revenue)}</strong></article>
      <article><span>Total budget</span><strong>{formatNpr(latest.totalBudget)}</strong></article>
      <article><span>Total expense</span><strong>{formatNpr(latest.expense)}</strong></article>
      <article><span>Gross profit</span><strong>{formatNpr(latest.grossProfit ?? latest.revenue-latest.expense)}</strong></article>
      <article><span>Revenue growth</span><strong>{growth === undefined ? "N/A" : `${growth.toFixed(1)}%`}</strong></article>
      <article><span>Budget utilization</span><strong>{latest.totalBudget ? `${(latest.expense/latest.totalBudget*100).toFixed(1)}%` : "N/A"}</strong></article>
    </div>}
    <div className={styles.grid}>
      <article className={`${styles.card} ${styles.wide}`}><header><div><span className={styles.eyebrow}>Annual performance</span><h2>Yearly Revenue</h2></div></header>
        {latest && yearly.length > 0 && <div className={styles.annualFacts}>
          <div><span>Current year</span><strong>{formatNpr(yearly.at(-1)!.revenue)}</strong></div>
          <div><span>Previous year</span><strong>{yearly.length > 1 ? formatNpr(yearly.at(-2)!.revenue) : "N/A"}</strong></div>
          <div><span>YoY growth</span><strong>{growth === undefined ? "N/A" : `${growth.toFixed(1)}%`}</strong></div>
          <div><span>Highest year</span><strong>{highest ? `${highest.year ?? highest.period} · ${formatNpr(highest.revenue)}` : "N/A"}</strong></div>
          <div><span>Annual average</span><strong>{formatNpr(annualAverage)}</strong></div>
        </div>}
        {yearlyData.length ? <div className={styles.chart}><ResponsiveContainer><AreaChart data={yearlyData} margin={{left:4,right:12}}><defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6366f1" stopOpacity={.3}/><stop offset="95%" stopColor="#6366f1" stopOpacity={.02}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis tickFormatter={compact}/><Tooltip formatter={moneyTooltip} contentStyle={tooltipStyle}/><Area type="monotone" dataKey="revenue" name="Revenue" stroke="#4f46e5" strokeWidth={3} fill="url(#revenueFill)"/></AreaChart></ResponsiveContainer></div> : <EmptyChart message="Yearly revenue data is unavailable for this dataset."/>}
      </article>
      <article className={styles.card}><header><div><span className={styles.eyebrow}>Seasonality</span><h2>Monthly Revenue</h2></div>{years.length > 0 && <select aria-label="Monthly revenue year" value={selectedYear} onChange={event=>setRequestedYear(Number(event.target.value))}>{years.map(year=><option key={year}>{year}</option>)}</select>}</header>
        {monthlyData.length ? <div className={styles.chart}><ResponsiveContainer><BarChart data={monthlyData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis tickFormatter={compact}/><Tooltip formatter={moneyTooltip} contentStyle={tooltipStyle}/><Bar dataKey="revenue" name="Revenue" fill="#818cf8" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></div> : <EmptyChart message="Monthly revenue data is unavailable. Add MONTHLY rows to enable this view."/>}
      </article>
      <article className={styles.card}><header><div><span className={styles.eyebrow}>Cost comparison</span><h2>Revenue vs Expense</h2></div></header>
        {yearlyData.length ? <div className={styles.chart}><ResponsiveContainer><BarChart data={yearlyData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis tickFormatter={compact}/><Tooltip formatter={moneyTooltip} contentStyle={tooltipStyle}/><Legend/><Bar dataKey="revenue" name="Revenue" fill="#4f46e5" radius={[4,4,0,0]}/><Bar dataKey="expense" name="Expense" fill="#f59e0b" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div> : <EmptyChart message="Revenue and expense history is unavailable."/>}
      </article>
      <article className={styles.card}><header><div><span className={styles.eyebrow}>Allocation control</span><h2>Budget vs Expense</h2></div></header>{chartRows.length ? <BudgetExpenseChart rows={chartRows}/> : <EmptyChart message="Budget comparison is unavailable."/>}</article>
      <article className={styles.card}><header><div><span className={styles.eyebrow}>Profitability</span><h2>Gross Profit</h2></div></header>
        {yearlyData.length ? <div className={styles.chart}><ResponsiveContainer><AreaChart data={yearlyData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis tickFormatter={compact}/><Tooltip formatter={moneyTooltip} contentStyle={tooltipStyle}/><Area type="monotone" dataKey="grossProfit" name="Gross Profit" stroke="#10b981" fill="#d1fae5" strokeWidth={3}/></AreaChart></ResponsiveContainer></div> : <EmptyChart message="Gross profit data is unavailable."/>}
      </article>
      <article className={styles.card}><header><div><span className={styles.eyebrow}>Volume trend</span><h2>Sales Units</h2></div></header>{chartRows.length ? <SalesUnitsChart rows={chartRows}/> : <EmptyChart message="Sales unit data is unavailable."/>}</article>
      <article className={`${styles.card} ${styles.wide}`}><header><div><span className={styles.eyebrow}>Momentum</span><h2>Year-over-Year Revenue Growth</h2></div></header>
        {yearlyData.length > 1 ? <div className={styles.chart}><ResponsiveContainer><LineChart data={growthData}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="label"/><YAxis tickFormatter={value=>`${value}%`}/><Tooltip formatter={value=>`${Number(Array.isArray(value) ? value[0] : value ?? 0).toFixed(1)}%`} contentStyle={tooltipStyle}/><Line type="monotone" dataKey="growth" name="Revenue Growth" stroke="#8b5cf6" strokeWidth={3} connectNulls/></LineChart></ResponsiveContainer></div> : <EmptyChart message="At least two yearly periods are required to calculate annual growth."/>}
      </article>
    </div>
  </section>;
}
