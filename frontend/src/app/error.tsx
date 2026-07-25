"use client";

import { useEffect } from "react";
import { Footer } from "@/components/Footer";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // In production, send this to your error-tracking service.
    // eslint-disable-next-line no-console
    console.error("Page Pulse error:", error);
  }, [error]);

  return (
    <div className="flex min-h-screen flex-col">
      <main className="flex flex-1 flex-col items-center justify-center px-4 py-12 text-center sm:px-6 lg:px-8">
        <div className="max-w-lg rounded-2xl border border-rose-450/40 bg-rose-550/10 p-8 card-shadow">
          <h1 className="font-serif text-4xl font-bold text-ink-900">Oops.</h1>
          <p className="mt-4 font-mono text-sm text-ink-800">
            The UI ran into an unexpected issue. Try again, or refresh the page.
          </p>
          {error.digest && (
            <p className="mt-2 font-mono text-xs text-ink-700/70">Error digest: {error.digest}</p>
          )}
          <button
            onClick={reset}
            className="mt-6 rounded-xl bg-amber-650 px-6 py-2 font-sans font-semibold text-white shadow-md transition-all hover:bg-ink-900"
          >
            Try again
          </button>
        </div>
      </main>
      <Footer />
    </div>
  );
}
