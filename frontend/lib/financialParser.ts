import { strFromU8, unzipSync } from "fflate";

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

export function deriveFinancialMetrics(financialRows: FinancialDataRow[]) {
  if (!financialRows.length) return null;
  const rows = [...financialRows].sort((a,b)=>a.period.localeCompare(b.period,undefined,{numeric:true}));
  const split = splitFinancialRows(rows);
  const activeSeries = split.yearly.length ? split.yearly : split.monthly.length ? split.monthly : rows;
  const latest = activeSeries.at(-1)!;
  const previous = activeSeries.at(-2);
  const growth = latest.revenueGrowthPercent ?? (previous?.revenue ? (latest.revenue-previous.revenue)/previous.revenue*100 : null);
  const rawCategories = [
    {name:"Marketing",amount:latest.marketingSpend}, {name:"Operations",amount:latest.operationsSpend},
    {name:"R&D",amount:latest.rndSpend}, {name:"Other",amount:latest.otherSpend},
  ];
  const categoryTotal = rawCategories.reduce((sum,item)=>sum+item.amount,0);
  const years = rows.map(row=>row.year).filter((year):year is number=>Boolean(year));
  return {
    rows, split, latest, growth,
    categories: rawCategories.map(item=>({...item,percent:categoryTotal ? item.amount/categoryTotal*100 : 0})),
    coverage: years.length ? `${Math.min(...years)}–${Math.max(...years)}` : `${rows[0].period}–${rows.at(-1)!.period}`,
    monthlyYears:[...new Set(split.monthly.map(row=>row.year).filter((year):year is number=>Boolean(year)))],
  };
}

export async function parseFinancialFile(file: File): Promise<FinancialDataRow[]> {
  const extension = file.name.split(".").pop()?.toLowerCase();
  if (extension !== "csv" && extension !== "xlsx") throw new Error("Unsupported file type. Choose a CSV or XLSX file.");
  if (file.size > 10_000_000) throw new Error("This file exceeds the 10 MB upload limit.");
  const bytes = new Uint8Array(await file.arrayBuffer());
  const rawRows = extension === "csv" ? parseCsv(strFromU8(bytes)) : parseXlsx(bytes);
  return normalizeFinancialRows(rawRows);
}

function parseCsv(source: string): Record<string, unknown>[] {
  const table: string[][] = [];
  let row: string[] = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (character === '"') {
      if (quoted && source[index + 1] === '"') {
        value += '"';
        index += 1;
      } else quoted = !quoted;
    } else if (character === "," && !quoted) {
      row.push(value);
      value = "";
    } else if ((character === "\n" || character === "\r") && !quoted) {
      if (character === "\r" && source[index + 1] === "\n") index += 1;
      row.push(value);
      if (row.some((cell) => cell.trim())) table.push(row);
      row = [];
      value = "";
    } else value += character;
  }
  if (quoted) throw new Error("This CSV contains an unterminated quoted value.");
  row.push(value);
  if (row.some((cell) => cell.trim())) table.push(row);
  const headers = table.shift()?.map((cell) => cell.replace(/^\uFEFF/, "").trim()) ?? [];
  if (!headers.length) return [];
  return table.map((cells) =>
    Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])),
  );
}

function xmlDocument(source: string, label: string): Document {
  const document = new DOMParser().parseFromString(source, "application/xml");
  if (document.querySelector("parsererror")) throw new Error(`The XLSX ${label} is invalid.`);
  return document;
}

function normalizeZipPath(base: string, target: string): string {
  const parts = (target.startsWith("/") ? target.slice(1) : `${base}/${target}`).split("/");
  const normalized: string[] = [];
  for (const part of parts) {
    if (!part || part === ".") continue;
    if (part === "..") normalized.pop();
    else normalized.push(part);
  }
  return normalized.join("/");
}

function columnIndex(reference: string): number {
  const letters = reference.match(/^[A-Z]+/i)?.[0].toUpperCase() ?? "A";
  return [...letters].reduce((total, letter) => total * 26 + letter.charCodeAt(0) - 64, 0) - 1;
}

function parseXlsx(bytes: Uint8Array): Record<string, unknown>[] {
  const archive = unzipSync(bytes, {
    filter: (entry) =>
      entry.originalSize <= 5_000_000 &&
      (/^xl\/(?:workbook|sharedStrings)\.xml$/.test(entry.name) ||
        entry.name === "xl/_rels/workbook.xml.rels" ||
        /^xl\/worksheets\/[^/]+\.xml$/.test(entry.name)),
  });
  const expandedSize = Object.values(archive).reduce((sum, item) => sum + item.length, 0);
  if (expandedSize > 20_000_000) throw new Error("The XLSX expands beyond the 20 MB safety limit.");
  const workbookBytes = archive["xl/workbook.xml"];
  const relationsBytes = archive["xl/_rels/workbook.xml.rels"];
  if (!workbookBytes || !relationsBytes) throw new Error("This XLSX is missing workbook metadata.");

  const workbook = xmlDocument(strFromU8(workbookBytes), "workbook metadata");
  const firstSheet = workbook.getElementsByTagName("sheet")[0];
  const relationshipId = firstSheet?.getAttribute("r:id") ?? firstSheet?.getAttribute("id");
  if (!relationshipId) throw new Error("This workbook does not contain a worksheet.");
  const relations = xmlDocument(strFromU8(relationsBytes), "relationships");
  const relation = [...relations.getElementsByTagName("Relationship")].find(
    (item) => item.getAttribute("Id") === relationshipId,
  );
  const target = relation?.getAttribute("Target");
  if (!target) throw new Error("The first worksheet could not be resolved.");
  const sheetPath = normalizeZipPath("xl", target);
  const sheetBytes = archive[sheetPath];
  if (!sheetBytes) throw new Error("The first worksheet is missing from this XLSX.");

  const sharedBytes = archive["xl/sharedStrings.xml"];
  const sharedStrings = sharedBytes
    ? [...xmlDocument(strFromU8(sharedBytes), "shared strings").getElementsByTagName("si")]
        .map((item) => [...item.getElementsByTagName("t")].map((text) => text.textContent ?? "").join(""))
    : [];
  const sheet = xmlDocument(strFromU8(sheetBytes), "worksheet");
  const table = [...sheet.getElementsByTagName("row")].map((rowElement) => {
    const cells: unknown[] = [];
    for (const cell of rowElement.getElementsByTagName("c")) {
      const index = columnIndex(cell.getAttribute("r") ?? "A1");
      const type = cell.getAttribute("t");
      const raw = cell.getElementsByTagName("v")[0]?.textContent ?? "";
      const inline = [...cell.getElementsByTagName("t")].map((item) => item.textContent ?? "").join("");
      if (type === "s") cells[index] = sharedStrings[Number(raw)] ?? "";
      else if (type === "inlineStr" || type === "str") cells[index] = inline || raw;
      else if (type === "b") cells[index] = raw === "1";
      else cells[index] = raw === "" ? "" : Number.isFinite(Number(raw)) ? Number(raw) : raw;
    }
    return cells;
  });
  const headers = (table.shift() ?? []).map((value) => String(value ?? "").trim());
  return table
    .filter((cells) => cells.some((value) => String(value ?? "").trim()))
    .map((cells) => Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
}

export const financialRequiredColumns = [...requiredColumns];
