"use client";

import { cn } from "@/lib/utils";

interface LoadingStateProps {
  className?: string;
}

const messages = [
  "Dialing into the web...",
  "Parsing the page...",
  "Counting headings...",
  "Checking SSL certificates...",
  "Crunching the score...",
];

export function LoadingState({ className }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-6 rounded-2xl border border-amber-450/30 bg-cream-50/90 p-10 text-center card-shadow backdrop-blur-sm",
        className,
      )}
    >
      <div className="relative h-16 w-16">
        <span className="absolute inset-0 rounded-full border-4 border-cream-200" />
        <span className="absolute inset-0 animate-spin rounded-full border-4 border-transparent border-t-amber-650" />
      </div>
      <div className="space-y-2">
        <p className="font-serif text-2xl font-semibold text-ink-900">Auditing...</p>
        <div className="h-6 overflow-hidden">
          <div className="animate-pulse">
            {messages.map((message, index) => (
              <p
                key={message}
                className="font-mono text-sm text-ink-700"
                style={{
                  animation: "pulse 2.5s infinite",
                  animationDelay: `${index * 0.5}s`,
                }}
              >
                {message}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
