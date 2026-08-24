"use client";
import { useId, useState } from "react";
import { demoFinancialRows } from "@/lib/demoData";
import {
  parseFinancialFile,
  type FinancialDataRow,
} from "@/lib/financialParser";
export type FinancialDatasetSource = "sample" | "file" | "manual";
type ParseState = "idle" | "selected" | "parsing" | "success" | "error";
interface ManualForm {
  period: string;
  totalBudget: string;
  revenue: string;
  expense: string;
  salesUnits: string;
  marketingSpend: string;
  operationsSpend: string;
  rndSpend: string;
  otherSpend: string;
}
const initialForm: ManualForm = {
  period: "2026-03",
  totalBudget: "3600000",
  revenue: "3820000",
  expense: "2830000",
  salesUnits: "2300",
  marketingSpend: "655000",
  operationsSpend: "1065000",
  rndSpend: "680000",
  otherSpend: "430000",
};
const bytes = (size: number) =>
  size < 1024
    ? `${size} B`
    : size < 1048576
      ? `${(size / 1024).toFixed(1)} KB`
      : `${(size / 1048576).toFixed(1)} MB`;
export function FinancialDataSource({
  demo,
  onApply,
}: {
  demo: boolean;
  onApply: (
    rows: FinancialDataRow[],
    source: FinancialDatasetSource,
    fileName?: string,
  ) => void;
}) {
  const [open, setOpen] = useState(false),
    [mode, setMode] = useState<FinancialDatasetSource>("sample");
  const [file, setFile] = useState<File | null>(null),
    [status, setStatus] = useState<ParseState>("idle"),
    [message, setMessage] = useState(""),
    [form, setForm] = useState(initialForm);
  const inputId = useId();
  const update = (key: keyof ManualForm, value: string) =>
    setForm((current) => ({ ...current, [key]: value }));
  const chooseFile = (next: File | null) => {
    setFile(next);
    setMessage("");
    if (!next) {
      setStatus("idle");
      return;
    }
    const ext = next.name.split(".").pop()?.toLowerCase();
    if (ext !== "csv" && ext !== "xlsx") {
      setStatus("error");
      setMessage("Unsupported file type. Choose a CSV or XLSX file.");
      return;
    }
    setStatus("selected");
  };
  async function loadFile() {
    if (!file) return;
    setStatus("parsing");
    setMessage("Reading financial data...");
    try {
      await new Promise((resolve) => window.setTimeout(resolve, 250));
      const rows = await parseFinancialFile(file);
      onApply(rows, "file", file.name);
      setStatus("success");
      setMessage(`${rows.length} rows loaded locally for prototype analysis.`);
    } catch (reason) {
      setStatus("error");
      setMessage(
        reason instanceof Error
          ? reason.message
          : "Unable to read this financial file.",
      );
    }
  }
  function applyManual() {
    const numeric = (key: keyof ManualForm, required = true) => {
      const value = Number(form[key]);
      if ((required && !form[key].trim()) || !Number.isFinite(value))
        throw new Error(`Enter a valid value for ${key}.`);
      return form[key].trim() ? value : 0;
    };
    try {
      const row: FinancialDataRow = {
        period: form.period.trim(),
        recordType: /^\d{4}-\d{1,2}$/.test(form.period.trim()) ? "MONTHLY" : "YEARLY",
        year: Number(form.period.trim().slice(0, 4)) || undefined,
        month: /^\d{4}-\d{1,2}$/.test(form.period.trim()) ? Number(form.period.trim().split("-")[1]) : undefined,
        totalBudget: numeric("totalBudget"),
        revenue: numeric("revenue"),
        expense: numeric("expense"),
        salesUnits: numeric("salesUnits"),
        marketingSpend: numeric("marketingSpend", false),
        operationsSpend: numeric("operationsSpend", false),
        rndSpend: numeric("rndSpend", false),
        otherSpend: numeric("otherSpend", false),
      };
      row.grossProfit = row.revenue - row.expense;
      if (!row.period) throw new Error("Enter a reporting period.");
      onApply([row], "manual");
      setOpen(false);
    } catch (reason) {
      setStatus("error");
      setMessage(
        reason instanceof Error ? reason.message : "Check the manual values.",
      );
    }
  }
  return (
    <>
      <button className="secondaryButton" onClick={() => setOpen(true)}>
        ＋ Financial Data Source
      </button>
      {open && (
        <div
          className="modalBackdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) setOpen(false);
          }}
        >
          <section
            aria-modal="true"
            className="financeModal"
            role="dialog"
            aria-labelledby="finance-title"
          >
            <header>
              <div>
                <span>Local prototype input</span>
                <h2 id="finance-title">Financial Data Source</h2>
              </div>
              <button
                aria-label="Close financial data source"
                onClick={() => setOpen(false)}
              >
                ×
              </button>
            </header>
            {!demo ? (
              <div className="integrationNotice">
                <strong>
                  Financial data input is available on the demo report.
                </strong>
                <p>
                  Open /reports/demo for browser-only CSV, XLSX, sample, and
                  manual analysis. Real workflow reports continue to use the
                  existing API.
                </p>
              </div>
            ) : (
              <>
                <nav aria-label="Financial data mode">
                  <button
                    className={mode === "sample" ? "active" : ""}
                    onClick={() => setMode("sample")}
                  >
                    Sample Dataset
                  </button>
                  <button
                    className={mode === "file" ? "active" : ""}
                    onClick={() => setMode("file")}
                  >
                    CSV / XLSX
                  </button>
                  <button
                    className={mode === "manual" ? "active" : ""}
                    onClick={() => setMode("manual")}
                  >
                    Manual Entry
                  </button>
                </nav>
                {mode === "sample" && (
                  <div className="sampleDataset">
                    <strong>2016–2026 financial performance sample</strong>
                    <p>
                      Includes yearly history plus monthly 2026 budget,
                      revenue, expense, profit, sales, and category data.
                    </p>
                    <button
                      className="primaryButton"
                      onClick={() => {
                        onApply(demoFinancialRows, "sample");
                        setOpen(false);
                      }}
                    >
                      Apply Sample Dataset
                    </button>
                  </div>
                )}
                {mode === "file" && (
                  <div className="filePanel">
                    <label className="fileDrop" htmlFor={inputId}>
                      <strong>
                        {file
                          ? "Choose another file"
                          : "Select a financial file"}
                      </strong>
                      <input
                        id={inputId}
                        accept=".csv,.xlsx"
                        type="file"
                        onChange={(event) =>
                          chooseFile(event.target.files?.[0] ?? null)
                        }
                      />
                      <small>
                        CSV or XLSX. The file stays in this browser tab and is
                        never uploaded.
                      </small>
                    </label>
                    {file && (
                      <dl className="fileFacts">
                        <div>
                          <dt>Filename</dt>
                          <dd>{file.name}</dd>
                        </div>
                        <div>
                          <dt>Type</dt>
                          <dd>{file.name.split(".").pop()?.toUpperCase()}</dd>
                        </div>
                        <div>
                          <dt>Size</dt>
                          <dd>{bytes(file.size)}</dd>
                        </div>
                      </dl>
                    )}
                    {message && (
                      <p className={`fileMessage ${status}`} role="status">
                        {status === "parsing" && <i aria-hidden="true" />}
                        {message}
                      </p>
                    )}
                    {status === "success" && (
                      <p className="localOnly">
                        Financial data loaded locally. Select another file to
                        replace it.
                      </p>
                    )}
                    <button
                      className="primaryButton"
                      disabled={
                        !file || status === "parsing" || status === "error"
                      }
                      onClick={() => void loadFile()}
                    >
                      {status === "parsing"
                        ? "Reading financial data..."
                        : "Load Financial Data"}
                    </button>
                  </div>
                )}
                {mode === "manual" && (
                  <div className="manualFinance">
                    {(
                      [
                        ["period", "Reporting Period"],
                        ["totalBudget", "Total Budget"],
                        ["revenue", "Revenue"],
                        ["expense", "Actual Expense"],
                        ["salesUnits", "Sales Units"],
                        ["marketingSpend", "Marketing Spend (optional)"],
                        ["operationsSpend", "Operations Spend (optional)"],
                        ["rndSpend", "R&D Spend (optional)"],
                        ["otherSpend", "Other Spend (optional)"],
                      ] as [keyof ManualForm, string][]
                    ).map(([key, label]) => (
                      <label key={key}>
                        {label}
                        <input
                          type={key === "period" ? "text" : "number"}
                          min={key === "period" ? undefined : 0}
                          value={form[key]}
                          onChange={(event) => update(key, event.target.value)}
                        />
                      </label>
                    ))}
                    {message && status === "error" && (
                      <p className="fileMessage error" role="alert">
                        {message}
                      </p>
                    )}
                    <button className="primaryButton" onClick={applyManual}>
                      Apply Manual Entry
                    </button>
                  </div>
                )}
                <p className="prototypeNote">
                  Local React memory only — no server upload or persistence.
                </p>
              </>
            )}
            <footer>
              <button
                className="secondaryButton"
                onClick={() => setOpen(false)}
              >
                {status === "success" ? "Close" : "Cancel"}
              </button>
            </footer>
          </section>
        </div>
      )}
    </>
  );
}
