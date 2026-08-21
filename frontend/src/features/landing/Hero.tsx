import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

function scrollToHowItWorks() {
  document.getElementById("how-it-works")?.scrollIntoView({ behavior: "smooth" });
}

export default function Hero() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen overflow-hidden flex flex-col items-center justify-center px-6 py-24">
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url('/images/lightning-bg.jpg')" }}
      />
      <div className="absolute inset-0 bg-background/80" />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative z-10 flex w-full flex-col items-center text-center"
      >
        <motion.button
          onClick={scrollToHowItWorks}
          whileHover={{ scale: 1.03 }}
          className="mb-6 flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs text-white/70 transition-colors hover:bg-white/10"
        >
          Explainable AI Code Intelligence
          <span aria-hidden="true">↓</span>
        </motion.button>

        <div className="relative">
          <h1 className="text-[9rem] leading-none font-display font-normal text-cracked">
            Strix
          </h1>
          <h1
            className="absolute inset-0 text-[9rem] leading-none font-display font-normal text-danger opacity-40 blur-2xl -z-10"
            aria-hidden="true"
          >
            Strix
          </h1>
        </div>

        <p className="mt-3 text-lg text-slate-300/70 tracking-wide">
          Every Algorithm Has a Story.
        </p>

        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate("/analyze")}
            className="rounded-xl border border-accent/40 bg-accent/10 px-8 py-3 text-sm font-medium text-white shadow-glow-magenta transition-colors hover:bg-accent/20"
          >
            Analyze your code
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            onClick={scrollToHowItWorks}
            className="rounded-xl border border-white/15 px-8 py-3 text-sm font-medium text-white/70 transition-colors hover:bg-white/5"
          >
            See how it works
          </motion.button>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-16 w-full max-w-3xl overflow-hidden rounded-2xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-md"
        >
          <div className="flex items-center gap-2 border-b border-white/10 px-4 py-3">
            <span className="h-3 w-3 rounded-full bg-danger/70" />
            <span className="h-3 w-3 rounded-full bg-primary/70" />
            <span className="h-3 w-3 rounded-full bg-toxic/70" />
            <span className="ml-2 font-mono text-xs text-white/40">bubble_sort.py</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2">
            <pre className="overflow-x-auto p-5 text-left font-mono text-xs text-white/70 sm:text-sm">
{`def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr`}
            </pre>
            <div className="flex flex-col gap-3 border-t border-white/10 p-5 sm:border-l sm:border-t-0">
              <div className="rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-left">
                <p className="text-xs text-white/50">Algorithm detected</p>
                <p className="text-sm font-medium text-primary-light">
                  Bubble Sort · High confidence
                </p>
              </div>
              <div className="rounded-lg border border-accent/30 bg-accent/10 px-3 py-2 text-left">
                <p className="text-xs text-white/50">Time complexity</p>
                <p className="text-sm font-medium text-accent-light">O(n²) worst case</p>
              </div>
              <div className="rounded-lg border border-toxic/30 bg-toxic/10 px-3 py-2 text-left">
                <p className="text-xs text-white/50">Space complexity</p>
                <p className="text-sm font-medium text-toxic-light">O(1) auxiliary</p>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}