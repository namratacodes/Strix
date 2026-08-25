import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import CodeEditorPanel, { DEFAULT_SNIPPETS } from "./CodeEditorPanel";
import ResultsPanel from "./ResultsPanel";
import { analyzeCode, type AnalysisResult, type SupportedLanguage } from "./api";
import AuthWidget from "../auth/AuthWidget";

export default function AnalysisPage() {
  const [language, setLanguage] =
    useState<SupportedLanguage>("python");

  const [code, setCode] = useState(
    DEFAULT_SNIPPETS.python
  );

  const mutation = useMutation<AnalysisResult, Error, void>({
    mutationFn: () => analyzeCode(code, language),
  });

  function handleLanguageChange(next: SupportedLanguage) {
    setLanguage(next);
    setCode(DEFAULT_SNIPPETS[next]);
  }

  return (
    <div className="min-h-screen bg-background bg-grid-dots px-6 py-10">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-3xl font-normal tracking-wide text-white">
            Analyze your code
          </h1>

          <div className="flex items-center gap-4">
            <a
              href="/history"
              className="text-xs text-white/40 transition-colors hover:text-white/70"
            >
              History
            </a>

            <AuthWidget />

            <a
              href="/"
              className="text-xs text-white/40 transition-colors hover:text-white/70"
            >
              ← Back home
            </a>
          </div>
        </div>

        {/* Editor + Results */}
        <div className="grid h-[70vh] grid-cols-1 gap-6 lg:grid-cols-2">

          <CodeEditorPanel
            value={code}
            onChange={setCode}
            onRun={() => mutation.mutate()}
            isRunning={mutation.isPending}
            language={language}
            onLanguageChange={handleLanguageChange}
          />

          <ResultsPanel
            result={mutation.data ?? null}
            isLoading={mutation.isPending}
            error={
              mutation.isError
                ? mutation.error.message
                : null
            }
          />

        </div>
      </div>
    </div>
  );
}