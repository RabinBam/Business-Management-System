export function ProgressBar({ value, max = 100, tone = "blue" }: { value: number; max?: number; tone?: "blue" | "green" | "amber" }) {
  const percentage = max > 0 ? Math.min(Math.max(value / max * 100, 0), 100) : 0;
  return <div className="numericProgress" role="progressbar" aria-valuemin={0} aria-valuemax={max} aria-valuenow={value}><i className={tone} style={{ width: `${percentage}%` }}/></div>;
}
