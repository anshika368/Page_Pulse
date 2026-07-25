import { AuditReport, ApiError } from "@/types/audit";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class AuditFetchError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public status: string,
  ) {
    super(message);
    this.name = "AuditFetchError";
  }
}

export async function auditUrl(url: string): Promise<AuditReport> {
  // Use the canonical /api/audit endpoint as documented in the README.
  const response = await fetch(`${API_URL}/api/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    let status = "error";

    try {
      const payload = (await response.json()) as ApiError;
      if (payload.detail) message = payload.detail;
      if (payload.status) status = payload.status;
    } catch {
      // Fallback to generic message if body is not JSON.
    }

    throw new AuditFetchError(message, response.status, status);
  }

  return response.json() as Promise<AuditReport>;
}
