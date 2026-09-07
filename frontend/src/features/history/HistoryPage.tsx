import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import ResultsPanel from "../analysis/ResultsPanel";
import { loginUrl } from "../auth/api";
import { useQueryClient } from "@tanstack/react-query";
import { fetchHistory, updateHistoryEntry, type HistoryEntry } from "./api";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function summaryLine(entry: HistoryEntry): string {
  const firstMatch = entry.result.algorithm_matches[0];

  if (firstMatch) {
    return firstMatch.name;
  }

  return "No pattern matched";
}

export default function HistoryPage() {
  const [selected, setSelected] = useState<HistoryEntry | null>(null);

  const {
    data,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["history"],
    queryFn: fetchHistory,
  });

  const isUnauthenticated =
    isError && (error as Error).message === "UNAUTHENTICATED";  const queryClient = useQueryClient();

  async function togglePin(entry: HistoryEntry, e: React.MouseEvent) {
    e.stopPropagation();
    await updateHistoryEntry(entry.id, { is_pinned: !entry.is_pinned });
    queryClient.invalidateQueries({ queryKey: ["history"] });
  }

  async function rename(entry: HistoryEntry, e: React.MouseEvent) {
    e.stopPropagation();
    const newLabel = window.prompt("Name this analysis:", entry.label ?? summaryLine(entry));
    if (newLabel === null) return;
    await updateHistoryEntry(entry.id, { label: newLabel });
    queryClient.invalidateQueries({ queryKey: ["history"] });
  }

  

  return (
    <div className="min-h-screen bg-background bg-grid-dots px-6 py-10">
      <div className="mx-auto max-w-6xl">

        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-heading text-3xl font-bold tracking-tight text-white">
            Your history
          </h1>

          <a
            href="/analyze"
            className="text-xs text-white/40 transition-colors hover:text-white/70"
          >
            ← Back to editor
          </a>
        </div>

        {/* Unauthenticated */}
        {isUnauthenticated && (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-8 text-center">
            <p className="text-sm text-white/60">
              Sign in to see your past analyses.
            </p>

            <a
              href={loginUrl()}
              className="mt-4 inline-block rounded-lg border border-white/15 px-4 py-1.5 text-xs text-white/70 transition-colors hover:bg-white/10"
            >
              Sign in with Google
            </a>
          </div>
        )}

        {/* Loading */}
        {isLoading && (
          <p className="text-sm text-white/40">
            Loading…
          </p>
        )}

        {/* Empty history */}
        {data && data.length === 0 && (
          <p className="text-sm text-white/40">
            No analyses yet — run one from the editor and it'll show up here.
          </p>
        )}

        {/* History */}
        {data && data.length > 0 && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

            {/* History list */}
            <div className="flex flex-col gap-3">
              {data.map((entry, i) => (
                <motion.button
                  key={entry.id}
                  onClick={() => setSelected(entry)}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    duration: 0.3,
                    delay: i * 0.05,
                  }}
                  className={`rounded-xl border px-4 py-3 text-left transition-colors ${
                    selected?.id === entry.id
                      ? "border-accent/50 bg-accent/10"
                      : "border-white/10 bg-white/5 hover:bg-white/10"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-white">
                      {entry.label ?? summaryLine(entry)}
                    </span>
                    <div className="flex shrink-0 items-center gap-2">
                      <button onClick={(e) => rename(entry, e)} className="text-[11px] text-white/40 hover:text-white/70">
                        Rename
                      </button>
                      <button onClick={(e) => togglePin(entry, e)} className="text-sm">
                        {entry.is_pinned ? "★" : "☆"}
                      </button>
                      <span className="text-[11px] text-white/40">{formatDate(entry.created_at)}</span>
                    </div>
                  </div>

                  <pre className="mt-2 overflow-hidden text-ellipsis whitespace-nowrap font-mono text-xs text-white/40">
                    {entry.source_code.trim().split("\n")[0]}
                  </pre>
                </motion.button>
              ))}
            </div>

            {/* Results */}
            <div className="h-[70vh]">
              <ResultsPanel
                result={selected?.result ?? null}
                isLoading={false}
                error={null}
                emptyMessage="Select a past analysis on the left to view its full story."
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}