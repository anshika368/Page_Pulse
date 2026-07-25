"use client";

import { cn } from "@/lib/utils";
import { AuditFetchError } from "@/lib/api";

interface ErrorDisplayProps {
  error: Error | null;
  className?: string;
}

export function ErrorDisplay({ error, className }: ErrorDisplayProps) {
  if (!error) return null;

  const title = error instanceof AuditFetchError ? `Error ${error.statusCode}` : "Something went wrong";
  const message = error.message || "An unexpected error occurred. Please try again.";

  return (
    <div
      role="alert"
      className={cn(
        "rounded-2xl border border-rose-450/40 bg-rose-550/10 p-6 text-ink-900 card-shadow",
        className,
      )}
    >
      <div className="flex items-start gap-4">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-rose-550 text-lg text-white">
          !
        </div>
        <div>
          <h3 className="font-serif text-xl font-semibold">{title}</h3>
          <p className="mt-1 font-mono text-sm leading-relaxed opacity-90">{message}</p>
          <p className="mt-3 text-xs opacity-70">
            Common causes: invalid URL, server timeout, DNS failure, or SSL certificate issues.
          </p>
        </div>
      </div>
    </div>
  );
}
