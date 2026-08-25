import Editor from "@monaco-editor/react";
import type { SupportedLanguage } from "./api";

export const DEFAULT_SNIPPETS: Record<SupportedLanguage, string> = {
  python: `def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
`,
  cpp: `int bubbleSort(int arr[], int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - 1; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
    return 0;
}
`,
  java: `public class Solution {
    public static int[] bubbleSort(int[] arr) {
        for (int i = 0; i < arr.length; i++) {
            for (int j = 0; j < arr.length - 1; j++) {
                if (arr[j] > arr[j+1]) {
                    int temp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = temp;
                }
            }
        }
        return arr;
    }
}
`,
};

const MONACO_LANGUAGE_MAP: Record<SupportedLanguage, string> = {
  python: "python",
  cpp: "cpp",
  java: "java",
};

const FILE_NAME_MAP: Record<SupportedLanguage, string> = {
  python: "solution.py",
  cpp: "solution.cpp",
  java: "Solution.java",
};

interface CodeEditorPanelProps {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  isRunning: boolean;
  language: SupportedLanguage;
  onLanguageChange: (language: SupportedLanguage) => void;
}

export default function CodeEditorPanel({
  value,
  onChange,
  onRun,
  isRunning,
  language,
  onLanguageChange,
}: CodeEditorPanelProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="h-3 w-3 rounded-full bg-danger/70" />
          <span className="h-3 w-3 rounded-full bg-primary/70" />
          <span className="h-3 w-3 rounded-full bg-toxic/70" />
          <span className="ml-1 font-mono text-xs text-white/40">{FILE_NAME_MAP[language]}</span>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as SupportedLanguage)}
            className="rounded-lg border border-white/15 bg-white/5 px-2 py-1 text-xs text-white/70 focus:outline-none"
            style={{ colorScheme: "dark" }}
          >
            <option value="python" style={{ backgroundColor: "#0a0a0f", color: "#fff" }}>
              Python
            </option>
            <option value="cpp" style={{ backgroundColor: "#0a0a0f", color: "#fff" }}>
              C++
            </option>
            <option value="java" style={{ backgroundColor: "#0a0a0f", color: "#fff" }}>
              Java
            </option>
          </select>
          <button
            onClick={onRun}
            disabled={isRunning}
            className="rounded-lg border border-accent/40 bg-accent/10 px-4 py-1.5 text-xs font-medium text-white shadow-glow-magenta transition-colors hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isRunning ? "Analyzing…" : "Run Analysis"}
          </button>
        </div>
      </div>
      <div className="flex-1">
        <Editor
          height="100%"
          language={MONACO_LANGUAGE_MAP[language]}
          theme="vs-dark"
          value={value}
          onChange={(v) => onChange(v ?? "")}
          options={{
            fontSize: 14,
            fontFamily: "JetBrains Mono, monospace",
            minimap: { enabled: false },
            padding: { top: 16 },
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  );
}