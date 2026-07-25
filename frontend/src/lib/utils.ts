import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export function scoreColor(score: number): string {
  if (score >= 80) return "text-teal-550";
  if (score >= 60) return "text-amber-650";
  return "text-rose-550";
}

export function scoreRingColor(score: number): string {
  if (score >= 80) return "stroke-teal-450";
  if (score >= 60) return "stroke-amber-450";
  return "stroke-rose-450";
}
