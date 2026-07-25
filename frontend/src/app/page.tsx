"use client";

import { useState, useCallback } from "react";
import { AuditForm } from "@/components/AuditForm";
import { AuditReportView } from "@/components/AuditReport";
import { ErrorDisplay } from "@/components/ErrorDisplay";
import { LoadingState } from "@/components/LoadingState";
import { Footer } from "@/components/Footer";
import { auditUrl } from "@/lib/api";
import { AuditReport } from "@/types/audit";

export default function Home() {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const handleAudit = useCallback(async (url: string) => {
    setLoading(true);
    setError(null);
    setReport(null);

    try {
      const data = await auditUrl(url);
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Unknown error"));
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex flex-1 flex-col items-center px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-5xl space-y-8">
          {/* Hero */}
          <div className="space-y-2 text-center">
            <p className="font-mono text-xs font-semibold uppercase tracking-[0.2em] text-amber-650">
              Vintage Web Diagnostics
            </p>
            <h1 className="font-serif text-5xl font-bold text-ink-900 sm:text-6xl">
              Page Pulse
            </h1>
            <p className="mx-auto max-w-xl font-sans text-ink-700">
              Drop in any URL. We’ll inspect its SEO, structure, SSL, links, images, and
              performance — then hand you a clean, cinematic report.
            </p>
          </div>

          {/* Form */}
          <AuditForm onSubmit={handleAudit} isLoading={loading} />

          {/* Results */}
          <div className="min-h-[120px]">
            {loading && <LoadingState />}
            {!loading && error && <ErrorDisplay error={error} />}
            {!loading && report && <AuditReportView report={report} />}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
