import { motion } from "framer-motion";
import type { ReasoningStep } from "./api";

interface ReasoningTimelineProps {
  steps: ReasoningStep[];
}

export default function ReasoningTimeline({ steps }: ReasoningTimelineProps) {
  return (
    <div className="space-y-3">
      {steps.map((step, i) => (
        <motion.div
          key={step.order}
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.35, delay: i * 0.08 }}
          className="flex gap-3 rounded-lg border border-white/10 bg-white/5 px-4 py-3"
        >
          <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/20 font-mono text-[10px] text-primary-light">
            {step.order + 1}
          </span>
          <div>
            <p className="text-sm font-medium text-white">{step.title}</p>
            <p className="mt-0.5 text-xs text-white/50">{step.detail}</p>
          </div>
        </motion.div>
      ))}
    </div>
  );
}