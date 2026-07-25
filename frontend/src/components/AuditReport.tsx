"use client";

import { AuditReport as AuditReportType } from "@/types/audit";
import { cn, formatDate, scoreColor } from "@/lib/utils";
import { ScoreRing } from "./ScoreRing";
import { MetricCard, type MetricCardProps } from "./MetricCard";

interface AuditReportProps {
  report: AuditReportType;
  className?: string;
}

function statusVariant(status: AuditReportType["status"]): MetricCardProps["variant"] {
  if (status === "ok") return "success";
  if (status === "timeout" || status === "unreachable") return "warning";
  return "danger";
}

function sslVariant(ssl: AuditReportType["ssl"]): MetricCardProps["variant"] {
  return ssl.valid ? "success" : "danger";
}

function formatBytes(kb: number | null): string {
  if (kb === null || kb === undefined) return "—";
  return kb >= 1024 ? `${(kb / 1024).toFixed(2)} MB` : `${kb.toFixed(1)} KB`;
}

export function AuditReportView({ report, className }: AuditReportProps) {
  const { seo, headings, links, images, performance, ssl, issues } = report;

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header card */}
      <div className="rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm sm:p-8">
        <div className="flex flex-col items-start gap-6 lg:flex-row lg:items-center">
          <ScoreRing score={report.score} />
          <div className="flex-1">
            <h2 className="font-serif text-2xl font-semibold text-ink-900 sm:text-3xl">
              {seo.title || "Untitled Page"}
            </h2>
            <p className="mt-1 font-mono text-sm text-amber-650 break-all">{report.final_url || report.url}</p>
            <p className="mt-2 font-sans text-sm text-ink-700">
              Audited on {formatDate(report.timestamp)}
            </p>
            <div className="mt-4 flex flex-wrap gap-3">
              <span
                className={cn(
                  "rounded-full px-3 py-1 font-mono text-xs font-medium",
                  report.status === "ok"
                    ? "bg-teal-450/15 text-teal-550"
                    : "bg-rose-450/15 text-rose-550",
                )}
              >
                {report.status.toUpperCase()}
              </span>
              {report.status_code && (
                <span className="rounded-full bg-cream-200 px-3 py-1 font-mono text-xs font-medium text-ink-900">
                  HTTP {report.status_code}
                </span>
              )}
              {report.response_time_ms && (
                <span className="rounded-full bg-cream-200 px-3 py-1 font-mono text-xs font-medium text-ink-900">
                  {report.response_time_ms.toFixed(0)} ms
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          label="Meta Title"
          value={seo.title_length || "—"}
          subtext={seo.title || "No title found"}
          variant={seo.title && seo.title_length >= 30 && seo.title_length <= 60 ? "success" : "warning"}
        />
        <MetricCard
          label="Meta Description"
          value={seo.description_length || "—"}
          subtext={
            seo.description
              ? `${seo.description.slice(0, 70)}${seo.description.length > 70 ? "..." : ""}`
              : "No description found"
          }
          variant={
            seo.description && seo.description_length >= 50 && seo.description_length <= 160
              ? "success"
              : "warning"
          }
        />
        <MetricCard
          label="SSL Certificate"
          value={ssl.valid ? "Valid" : "Invalid"}
          subtext={
            ssl.valid
              ? ssl.expires_in_days !== null
                ? `${ssl.expires_in_days} days left`
                : "Verified"
              : "Could not verify"
          }
          variant={sslVariant(ssl)}
        />
        <MetricCard
          label="Page Weight"
          value={formatBytes(performance.page_size_kb)}
          subtext={
            performance.page_size_kb && performance.page_size_kb < 1500
              ? "Lightweight"
              : "Could be optimized"
          }
          variant={
            performance.page_size_kb && performance.page_size_kb < 1500 ? "success" : "warning"
          }
        />
      </div>

      {/* Content structure */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm">
          <h3 className="font-serif text-xl font-semibold text-ink-900">Heading Structure</h3>
          <div className="mt-4 grid grid-cols-3 gap-3">
            {(["h1", "h2", "h3", "h4", "h5", "h6"] as const).map((tag) => (
              <div
                key={tag}
                className={cn(
                  "rounded-xl border p-3 text-center",
                  tag === "h1" && headings.h1 === 1
                    ? "border-teal-450/40 bg-teal-450/10"
                    : tag === "h1" && headings.h1 !== 1
                      ? "border-rose-450/40 bg-rose-450/10"
                      : "border-ink-900/10 bg-white",
                )}
              >
                <span className="font-mono text-xs font-bold uppercase text-ink-700">{tag}</span>
                <div className="mt-1 font-mono text-2xl font-semibold text-ink-900">
                  {headings[tag]}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm">
          <h3 className="font-serif text-xl font-semibold text-ink-900">Links &amp; Images</h3>
          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-between rounded-xl border border-ink-900/10 bg-white p-3">
              <span className="font-mono text-xs uppercase text-ink-700">Internal Links</span>
              <span className="font-mono text-lg font-semibold text-ink-900">{links.internal}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl border border-ink-900/10 bg-white p-3">
              <span className="font-mono text-xs uppercase text-ink-700">External Links</span>
              <span className="font-mono text-lg font-semibold text-ink-900">{links.external}</span>
            </div>
            <div
              className={cn(
                "flex items-center justify-between rounded-xl border p-3",
                images.without_alt === 0
                  ? "border-teal-450/40 bg-teal-450/10"
                  : "border-amber-450/40 bg-amber-450/10",
              )}
            >
              <span className="font-mono text-xs uppercase text-ink-700">Images Missing Alt</span>
              <span className="font-mono text-lg font-semibold text-ink-900">{images.without_alt} / {images.total}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SEO checklist */}
      <div className="rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm">
        <h3 className="font-serif text-xl font-semibold text-ink-900">SEO Checklist</h3>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Canonical", ok: seo.has_canonical },
            { label: "Open Graph", ok: seo.has_open_graph },
            { label: "Twitter Card", ok: seo.has_twitter_card },
            { label: "Favicon", ok: seo.has_favicon },
          ].map((item) => (
            <div
              key={item.label}
              className={cn(
                "flex items-center gap-3 rounded-xl border p-3",
                item.ok
                  ? "border-teal-450/40 bg-teal-450/10"
                  : "border-amber-450/40 bg-amber-450/10",
              )}
            >
              <span
                className={cn(
                  "flex h-6 w-6 items-center justify-center rounded-full text-sm",
                  item.ok ? "bg-teal-450 text-white" : "bg-amber-450 text-white",
                )}
              >
                {item.ok ? "✓" : "−"}
              </span>
              <span className="font-mono text-sm font-medium text-ink-900">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Issues */}
      <div className="rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm">
        <h3 className={cn("font-serif text-xl font-semibold", scoreColor(report.score))}>
          {report.score >= 80 ? "Highlights" : report.score >= 60 ? "Notes" : "Issues to Fix"}
        </h3>
        <ul className="mt-4 space-y-2">
          {issues.map((issue, index) => (
            <li
              key={index}
              className="flex items-start gap-3 rounded-xl border border-ink-900/10 bg-white p-3"
            >
              <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-amber-650" />
              <span className="font-mono text-sm text-ink-800">{issue}</span>
            </li>
          ))}
          {issues.length === 0 && (
            <li className="rounded-xl border border-teal-450/40 bg-teal-450/10 p-3 font-mono text-sm text-teal-550">
              No issues found.
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}
