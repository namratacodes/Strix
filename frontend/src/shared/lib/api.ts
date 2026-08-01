/**
 * Central API client configuration.
 *
 * Kept as a single module so every feature slice (editor, analysis, auth)
 * imports the same base URL and error-handling convention rather than
 * each hand-rolling its own fetch wrapper.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface HealthResponse {
  status: string;
  service: string;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}
