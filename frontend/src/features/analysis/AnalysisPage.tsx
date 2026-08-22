import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import CodeEditorPanel, { DEFAULT_SNIPPET } from "./CodeEditorPanel";
import ResultsPanel from "./ResultsPanel";
import { analyzeCode, type AnalysisResult } from "./api";

export default function AnalysisPage() {
  const [code, setCode] = useState(DEFAULT_SNIPPET);

  const mutation = useMutation<AnalysisResult, Error, string>({
    mutationFn: analyzeCode,
  });

  return (
    <div className="min-h-screen bg-background bg-grid-dots px-6 py-10">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-3xl font-normal tracking-wide text-white">
            Analyze your code
          </h1>
          <a href="/" className="text-xs text-white/40 hover:text-white/70">
            ← Back home
          </a>
        </div>

        <div className="grid h-[70vh] grid-cols-1 gap-6 lg:grid-cols-2">
          <CodeEditorPanel
            value={code}
            onChange={setCode}
            onRun={() => mutation.mutate(code)}
            isRunning={mutation.isPending}
          />
          <ResultsPanel
            result={mutation.data ?? null}
            isLoading={mutation.isPending}
            error={mutation.isError ? mutation.error.message : null}
          />
        </div>
      </div>
    </div>
  );
}