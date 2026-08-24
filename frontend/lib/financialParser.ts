import * as XLSX from "xlsx";

export interface FinancialDataRow {
  period: string;
  totalBudget: number;
  revenue: number;
  expense: number;
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
    return {
      period,
      totalBudget: values.Total_Budget_NPR as number,
      revenue: values.Revenue_NPR as number,
      expense: values.Expense_NPR as number,
      salesUnits: values.Sales_Units as number,
      marketingSpend: optionalNumber(row, "Marketing_Spend_NPR"),
      operationsSpend: optionalNumber(row, "Operations_Spend_NPR"),
      rndSpend: optionalNumber(row, "RnD_Spend_NPR"),
      otherSpend: optionalNumber(row, "Other_Spend_NPR"),
    };
  });
  return rows.sort((a, b) => a.period.localeCompare(b.period, undefined, { numeric: true }));
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
