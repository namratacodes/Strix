import Editor from "@monaco-editor/react";

export const DEFAULT_SNIPPET = `def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
`;

interface CodeEditorPanelProps {
  value: string;
  onChange: (value: string) => void;
  onRun: () => void;
  isRunning: boolean;
}

export default function CodeEditorPanel({
  value,
  onChange,
  onRun,
  isRunning,
}: CodeEditorPanelProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-white/10 bg-white/5">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full bg-danger/70" />
          <span className="h-3 w-3 rounded-full bg-primary/70" />
          <span className="h-3 w-3 rounded-full bg-toxic/70" />
          <span className="ml-2 font-mono text-xs text-white/40">solution.py</span>
        </div>
        <button
          onClick={onRun}
          disabled={isRunning}
          className="rounded-lg border border-accent/40 bg-accent/10 px-4 py-1.5 text-xs font-medium text-white shadow-glow-magenta transition-colors hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isRunning ? "Analyzing…" : "Run Analysis"}
        </button>
      </div>
      <div className="flex-1">
        <Editor
          height="100%"
          defaultLanguage="python"
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