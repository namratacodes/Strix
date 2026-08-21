import { useState } from "react";
import { motion } from "framer-motion";
import FogLayer from "./FogLayer";


export default function AnalysisPage() {
  const [analyzed, setAnalyzed] = useState(false);
  const tint = analyzed ? "toxic" : "danger";

  return (
    <div className="relative min-h-[200vh] text-white">
      <FogLayer tint={tint} />
      
      <div className="relative z-10 flex min-h-screen flex-col items-center justify-center px-6 text-center">
        <h2 className="text-3xl font-display tracking-wide">
          {analyzed ? "Analysis complete" : "Awaiting your code"}
        </h2>
        <p className="mt-2 max-w-md text-white/60">
          {analyzed
            ? "STRIX has traced the story behind your algorithm."
            : "The code editor lands here in the next milestone. For now, this proves the fog environment and the red-to-green analysis state."}
        </p>

        {/* Temporary demo control -- real trigger becomes "Run Analysis" once Monaco + API are wired in */}
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setAnalyzed((v) => !v)}
          className="mt-8 rounded-xl border border-white/20 bg-white/5 px-6 py-2 text-sm text-white/80 hover:bg-white/10"
        >
          {analyzed ? "Reset demo" : "Simulate analysis (demo)"}
        </motion.button>
      </div>

      <div className="relative z-10 flex min-h-screen items-center justify-center px-6">
        <div className="max-w-xl rounded-2xl border border-white/10 bg-white/5 p-8 text-center backdrop-blur-sm">
          <p className="text-white/70">
            Scroll checkpoint — code editor and reasoning timeline panels arrive here in upcoming milestones.
          </p>
        </div>
      </div>
    </div>
  );
}