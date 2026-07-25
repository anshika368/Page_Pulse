import { cn } from "@/lib/utils";

export interface MetricCardProps {
  label: string;
  value: React.ReactNode;
  subtext?: string;
  variant?: "default" | "success" | "warning" | "danger";
  className?: string;
}

const variantStyles = {
  default: "border-ink-900/10 bg-cream-50/80",
  success: "border-teal-450/40 bg-teal-450/10",
  warning: "border-amber-450/40 bg-amber-450/10",
  danger: "border-rose-450/40 bg-rose-450/10",
};

export function MetricCard({
  label,
  value,
  subtext,
  variant = "default",
  className,
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border p-4 card-shadow backdrop-blur-sm",
        variantStyles[variant],
        className,
      )}
    >
      <p className="font-sans text-xs font-semibold uppercase tracking-wider text-ink-700">
        {label}
      </p>
      <div className="mt-2 font-mono text-2xl font-semibold text-ink-900">{value}</div>
      {subtext && (
        <p className="mt-1 font-mono text-xs text-ink-700/80">{subtext}</p>
      )}
    </div>
  );
}
