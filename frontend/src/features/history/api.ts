import type { AnalysisResult } from "../analysis/api";

export interface HistoryEntry {
  id: string;
  user_id: string;
  source_code: string;
  language: string;
  result: AnalysisResult;
  created_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchHistory(): Promise<HistoryEntry[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/history`, { credentials: "include" });
  if (res.status === 401) {
    throw new Error("UNAUTHENTICATED");
  }
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}