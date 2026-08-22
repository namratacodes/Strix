import { motion } from "framer-motion";
import type { AnalysisResult, ConfidenceLevel } from "./api";
import ReasoningTimeline from "./ReasoningTimeline";

interface ResultsPanelProps {
  result: AnalysisResult | null;
  isLoading: boolean;
  error: string | null;
}

// Confidence acts as a traffic light throughout the results: high = trust
// it (toxic green), medium = caution (amber), low = uncertain (red) --
// consistent with the confidence-first philosophy from the backend engine.
const CONFIDENCE_STYLES: Record<ConfidenceLevel, string> = {
  high: "border-toxic/40 bg-toxic/10 text-toxic-light",
  medium: "border-primary/40 bg-primary/10 text-primary-light",
  low: "border-danger/40 bg-danger/10 text-danger-light",
};

export default function ResultsPanel({ result, isLoading, error }: ResultsPanelProps) {
  if (isLoading) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
        <motion.div
          className="h-3 w-3 rounded-full bg-primary"
          animate={{ opacity: [0.3, 1, 0.3], scale: [0.9, 1.2, 0.9] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: "easeInOut" }}
        />
        <p className="text-sm text-white/50">STRIX is reasoning through your code…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-danger/30 bg-danger/5 p-8 text-center">
        <p className="text-sm text-danger-light">{error}</p>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex h-full flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
        <p className="text-sm text-white/40">
          Paste code on the left and click "Run Analysis" to see the story behind it.
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col gap-6 overflow-y-auto rounded-2xl border border-white/10 bg-white/5 p-6">
      <section>
        <h3 className="text-xs uppercase tracking-wide text-white/40">Algorithm</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {result.algorithm_matches.length === 0 && (
            <span className="text-sm text-white/50">No known pattern confidently matched.</span>
          )}
          {result.algorithm_matches.map((m) => (
            <span
              key={m.name}
              title={m.rationale}
              className={`rounded-lg border px-3 py-1.5 text-sm font-medium ${CONFIDENCE_STYLES[m.confidence]}`}
            >
              {m.name} · {m.confidence} confidence
            </span>
          ))}
        </div>
      </section>

      {result.complexity && (
        <section>
          <h3 className="text-xs uppercase tracking-wide text-white/40">Complexity</h3>
          <div className="mt-2 grid grid-cols-2 gap-3">
            <div
              className={`rounded-lg border px-3 py-2 ${CONFIDENCE_STYLES[result.complexity.worst_case.confidence]}`}
            >
              <p className="text-[11px] text-white/50">Time (worst case)</p>
              <p className="text-lg font-semibold">
                {result.complexity.worst_case.complexity_class}
              </p>
            </div>
            <div
              className={`rounded-lg border px-3 py-2 ${CONFIDENCE_STYLES[result.complexity.space.confidence]}`}
            >
              <p className="text-[11px] text-white/50">Space</p>
              <p className="text-lg font-semibold">{result.complexity.space.complexity_class}</p>
            </div>
          </div>
        </section>
      )}

      {result.explanation && (
        <section>
          <h3 className="text-xs uppercase tracking-wide text-white/40">Explanation</h3>
          <p className="mt-2 text-sm leading-relaxed text-white/70">{result.explanation}</p>
        </section>
      )}

      <section>
        <h3 className="text-xs uppercase tracking-wide text-white/40">Reasoning Timeline</h3>
        <div className="mt-2">
          <ReasoningTimeline steps={result.reasoning_timeline} />
        </div>
      </section>
    </div>
  );
}