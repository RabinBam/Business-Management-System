import * as XLSX from "xlsx";

export interface FinancialDataRow {
  recordType?: "YEARLY" | "MONTHLY";
  period: string;
  year?: number;
  month?: number;
  totalBudget: number;
  revenue: number;
  expense: number;
  grossProfit?: number;
  revenueGrowthPercent?: number;
  salesUnits: number;
  marketingSpend: number;
  operationsSpend: number;
  rndSpend: number;
  otherSpend: number;
}

const requiredColumns = ["Period", "Total_Budget_NPR", "Revenue_NPR", "Expense_NPR", "Sales_Units"] as const;
const numericColumns = ["Total_Budget_NPR", "Revenue_NPR", "Expense_NPR", "Sales_Units"] as const;

function numberFrom(value: unknown): number | null {
  if (typeof value === "number") return Number.isFinite(value) ? value : null;
  if (typeof value !== "string" || !value.trim()) return null;
  const normalized = value.replace(/NPR/gi, "").replace(/[,_\s]/g, "").trim();
  const parsed = Number(normalized);
  return Number.isFinite(parsed) ? parsed : null;
}

function optionalNumber(row: Record<string, unknown>, column: string): number {
  const value = row[column];
  if (value === "" || value === null || value === undefined) return 0;
  const parsed = numberFrom(value);
  if (parsed === null) throw new Error(`Invalid numeric value in ${column}.`);
  return parsed;
}

function optionalNullableNumber(row: Record<string, unknown>, column: string): number | undefined {
  const value = row[column];
  if (value === "" || value === null || value === undefined) return undefined;
  const parsed = numberFrom(value);
  if (parsed === null) throw new Error(`Invalid numeric value in ${column}.`);
  return parsed;
}

export function normalizeFinancialRows(rawRows: Record<string, unknown>[]): FinancialDataRow[] {
  if (!rawRows.length) throw new Error("This file contains no financial data rows.");
  const columns = new Set(rawRows.flatMap((row) => Object.keys(row).map((key) => key.trim())));
  const missing = requiredColumns.filter((column) => !columns.has(column));
  if (missing.length) throw new Error(`This file is missing required columns: ${missing.join(", ")}`);

  const rows = rawRows.map((raw, index) => {
    const row = Object.fromEntries(Object.entries(raw).map(([key, value]) => [key.trim(), value]));
    const period = String(row.Period ?? "").trim();
    if (!period) throw new Error(`Row ${index + 2} is missing Period.`);
    const values = Object.fromEntries(numericColumns.map((column) => [column, numberFrom(row[column])]));
    const invalid = numericColumns.find((column) => values[column] === null);
    if (invalid) throw new Error(`Row ${index + 2} has invalid numeric data in ${invalid}.`);
    const explicitType = String(row.Record_Type ?? "").trim().toUpperCase();
    if (explicitType && explicitType !== "YEARLY" && explicitType !== "MONTHLY") throw new Error(`Row ${index + 2} has invalid Record_Type. Use YEARLY or MONTHLY.`);
    const inferredType = /^\d{4}-\d{1,2}$/.test(period) ? "MONTHLY" : /^\d{4}$/.test(period) ? "YEARLY" : undefined;
    const recordType = (explicitType || inferredType) as FinancialDataRow["recordType"];
    const derivedYear = Number(period.slice(0, 4));
    const year = optionalNullableNumber(row, "Year") ?? (Number.isInteger(derivedYear) ? derivedYear : undefined);
    const derivedMonth = /^\d{4}-(\d{1,2})$/.exec(period)?.[1];
    const month = optionalNullableNumber(row, "Month") ?? (derivedMonth ? Number(derivedMonth) : undefined);
    return {
      recordType,
      period,
      year,
      month,
      totalBudget: values.Total_Budget_NPR as number,
      revenue: values.Revenue_NPR as number,
      expense: values.Expense_NPR as number,
      grossProfit: optionalNullableNumber(row, "Gross_Profit_NPR"),
      revenueGrowthPercent: optionalNullableNumber(row, "Revenue_Growth_Pct"),
      salesUnits: values.Sales_Units as number,
      marketingSpend: optionalNumber(row, "Marketing_Spend_NPR"),
      operationsSpend: optionalNumber(row, "Operations_Spend_NPR"),
      rndSpend: optionalNumber(row, "RnD_Spend_NPR"),
      otherSpend: optionalNumber(row, "Other_Spend_NPR"),
    };
  });
  return rows.sort((a, b) => (a.year ?? 0) - (b.year ?? 0) || (a.month ?? 0) - (b.month ?? 0) || a.period.localeCompare(b.period, undefined, { numeric: true }));
}

export function splitFinancialRows(rows: FinancialDataRow[]): { yearly: FinancialDataRow[]; monthly: FinancialDataRow[] } {
  const explicitYearly = rows.filter((row) => row.recordType === "YEARLY");
  const monthlyRows = rows.filter((row) => row.recordType === "MONTHLY");
  if (explicitYearly.length) return { yearly: explicitYearly, monthly: monthlyRows };
  const grouped = new Map<number, FinancialDataRow[]>();
  monthlyRows.forEach((row) => { if (row.year) grouped.set(row.year, [...(grouped.get(row.year) ?? []), row]); });
  const yearlyRows = [...grouped.entries()].map(([year, items]) => ({
    recordType: "YEARLY" as const, period: String(year), year,
    totalBudget: items.reduce((sum,row)=>sum+row.totalBudget,0), revenue: items.reduce((sum,row)=>sum+row.revenue,0), expense: items.reduce((sum,row)=>sum+row.expense,0),
    grossProfit: items.reduce((sum,row)=>sum+(row.grossProfit ?? row.revenue-row.expense),0), salesUnits: items.reduce((sum,row)=>sum+row.salesUnits,0),
    marketingSpend: items.reduce((sum,row)=>sum+row.marketingSpend,0), operationsSpend: items.reduce((sum,row)=>sum+row.operationsSpend,0), rndSpend: items.reduce((sum,row)=>sum+row.rndSpend,0), otherSpend: items.reduce((sum,row)=>sum+row.otherSpend,0),
  }));
  return { yearly: yearlyRows, monthly: monthlyRows };
}

export async function parseFinancialFile(file: File): Promise<FinancialDataRow[]> {
  const extension = file.name.split(".").pop()?.toLowerCase();
  if (extension !== "csv" && extension !== "xlsx") throw new Error("Unsupported file type. Choose a CSV or XLSX file.");
  // Keep CSV period labels such as "2026-01" as text instead of Excel date serials.
  const workbook = XLSX.read(await file.arrayBuffer(), { type: "array", raw: true });
  const firstSheet = workbook.SheetNames[0];
  if (!firstSheet) throw new Error("This workbook does not contain a worksheet.");
  const rawRows = XLSX.utils.sheet_to_json<Record<string, unknown>>(workbook.Sheets[firstSheet], { defval: "", raw: true });
  return normalizeFinancialRows(rawRows);
}

export const financialRequiredColumns = [...requiredColumns];
