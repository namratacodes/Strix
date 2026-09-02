import { motion } from "framer-motion";

const SCALE = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(2^n)", "O(n!)"];

const COLOR_BY_INDEX = [
  "#39FF88", // O(1) - toxic green
  "#39FF88",
  "#8CFFC0",
  "#F5A623", // amber
  "#F5A623",
  "#FF2E7E", // magenta
  "#FF3B3B", // danger red
];

interface ComplexityGraphProps {
  timeClass: string;
  spaceClass: string;
}

function markerPosition(cls: string): number {
  const i = SCALE.indexOf(cls);
  return i === -1 ? 0 : (i / (SCALE.length - 1)) * 100;
}

export default function ComplexityGraph({ timeClass, spaceClass }: ComplexityGraphProps) {
  const timeIndex = SCALE.indexOf(timeClass);
  const spaceIndex = SCALE.indexOf(spaceClass);

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-4">
      {/* Scale track */}
      <div className="relative mt-2 h-2 rounded-full bg-white/10">
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: `linear-gradient(to right, ${COLOR_BY_INDEX.join(", ")})`,
            opacity: 0.25,
          }}
        />
        {timeIndex !== -1 && (
          <motion.div
            className="absolute top-1/2 h-4 w-4 -translate-y-1/2 rounded-full border-2 border-background"
            style={{ background: COLOR_BY_INDEX[timeIndex], left: `calc(${markerPosition(timeClass)}% - 8px)` }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 18 }}
            title={`Time: ${timeClass}`}
          />
        )}
        {spaceIndex !== -1 && spaceClass !== timeClass && (
          <motion.div
            className="absolute top-1/2 h-3 w-3 -translate-y-1/2 rounded-full border-2 border-background opacity-70"
            style={{ background: COLOR_BY_INDEX[spaceIndex], left: `calc(${markerPosition(spaceClass)}% - 6px)` }}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 18, delay: 0.1 }}
            title={`Space: ${spaceClass}`}
          />
        )}
      </div>

      {/* Scale labels */}
      <div className="mt-2 flex justify-between text-[10px] text-white/30">
        {SCALE.map((cls) => (
          <span key={cls} className={cls === timeClass ? "font-semibold text-white/80" : ""}>
            {cls}
          </span>
        ))}
      </div>

      <div className="mt-3 flex gap-4 text-[11px] text-white/50">
        <span className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full" style={{ background: COLOR_BY_INDEX[timeIndex] ?? "#888" }} />
          Time
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full opacity-70" style={{ background: COLOR_BY_INDEX[spaceIndex] ?? "#888" }} />
          Space
        </span>
      </div>
    </div>
  );
}