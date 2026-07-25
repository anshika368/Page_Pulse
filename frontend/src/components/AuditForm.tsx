"use client";

import { useState, FormEvent } from "react";
import { cn } from "@/lib/utils";

interface AuditFormProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
  className?: string;
}

export function AuditForm({ onSubmit, isLoading, className }: AuditFormProps) {
  const [url, setUrl] = useState("");
  const [touched, setTouched] = useState(false);

  const trimmed = url.trim();
  const isValid =
    touched &&
trimmed.length > 0 &&
    /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([\/\w .-]*)*\/?$/.test(trimmed);
  const showError = touched && !isValid && trimmed.length > 0;

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    setTouched(true);
    if (!trimmed) return;
    onSubmit(trimmed);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={cn(
        "flex flex-col gap-4 rounded-2xl border border-ink-900/10 bg-cream-50/90 p-6 card-shadow backdrop-blur-sm sm:flex-row sm:items-start sm:p-8",
        className,
      )}
      noValidate
    >
      <div className="flex-1">
        <label htmlFor="url" className="sr-only">
          Website URL
        </label>
        <input
          id="url"
          type="url"
          inputMode="url"
          name="url"
          placeholder="https://example.com"
          value={url}
          onChange={(e) => {
            setUrl(e.target.value);
            if (!touched) setTouched(true);
          }}
          disabled={isLoading}
          className={cn(
            "w-full rounded-xl border bg-white px-4 py-3 font-mono text-ink-900 placeholder:text-ink-700/40 focus:outline-none focus:ring-2 focus:ring-amber-450",
            showError
              ? "border-rose-450 focus:ring-rose-450"
              : "border-ink-900/10 focus:ring-amber-450",
          )}
          aria-invalid={showError}
          aria-describedby={showError ? "url-error" : undefined}
        />
        {showError && (
          <p id="url-error" className="mt-2 font-mono text-xs text-rose-550">
            Please enter a valid URL.
          </p>
        )}
      </div>
      <button
        type="submit"
        disabled={isLoading || !trimmed}
        className="shrink-0 rounded-xl bg-amber-650 px-8 py-3 font-sans font-semibold text-white shadow-md transition-all hover:bg-ink-900 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isLoading ? "Auditing..." : "Pulse Check"}
      </button>
    </form>
  );
}
