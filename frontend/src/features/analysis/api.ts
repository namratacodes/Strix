/**
 * Types mirror the backend's domain entities (Milestone 2) and the
 * AnalysisResult returned by POST /api/v1/analyze (Milestone 8).
 */

export type ConfidenceLevel = "high" | "medium" | "low";

export interface AlgorithmMatch {
  name: string;
  confidence: ConfidenceLevel;
  rationale: string;
  location: { line_start: number; line_end: number } | null;
}

export interface ComplexityEstimate {
  complexity_class: string;
  rationale: string;
  confidence: ConfidenceLevel;
}

export interface ComplexityResult {
  best_case: ComplexityEstimate;
  average_case: ComplexityEstimate;
  worst_case: ComplexityEstimate;
  space: ComplexityEstimate;
}

export interface ReasoningStep {
  order: number;
  title: string;
  detail: string;
}

export interface AnalysisResult {
  submission_id: string;
  algorithm_matches: AlgorithmMatch[];
  complexity: ComplexityResult | null;
  reasoning_timeline: ReasoningStep[];
  explanation: string | null;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function analyzeCode(sourceCode: string): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_code: sourceCode, language: "python" }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Analysis failed (${res.status})`);
  }

  return res.json();
}