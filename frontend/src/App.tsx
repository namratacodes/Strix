import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { fetchHealth } from "@/shared/lib/api";

export default function App() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
  });

  return (
    <div className="min-h-screen flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="rounded-2xl border border-border bg-surface backdrop-blur-xs px-10 py-8 text-center max-w-md"
      >
        <h1 className="text-3xl font-semibold tracking-tight">
          STRIX
        </h1>
        <p className="mt-1 text-sm text-white/50">Every Algorithm Has a Story.</p>

        <div className="mt-6 text-sm">
          {isLoading && <span className="text-white/50">Checking backend connection…</span>}
          {isError && (
            <span className="text-red-400">
              Could not reach backend. Is it running on port 8000?
            </span>
          )}
          {data && (
            <span className="text-accent">
              ✓ Backend connected — {data.service} is {data.status}
            </span>
          )}
        </div>
      </motion.div>
    </div>
  );
}
