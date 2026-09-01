import { useEffect, useState } from "react";

interface TypewriterTextProps {
  text: string;
  typingSpeedMs?: number;
  pauseMs?: number;
  deletingSpeedMs?: number;
}

/**
 * Loops through: type out `text` character by character, pause, delete
 * character by character, pause, repeat. Pure timer-based, no external
 * animation library needed for this effect.
 */
export default function TypewriterText({
  text,
  typingSpeedMs = 60,
  pauseMs = 1800,
  deletingSpeedMs = 35,
}: TypewriterTextProps) {
  const [displayed, setDisplayed] = useState("");
  const [phase, setPhase] = useState<"typing" | "pausing" | "deleting">("typing");

  useEffect(() => {
    if (phase === "typing") {
      if (displayed.length < text.length) {
        const timeout = setTimeout(
          () => setDisplayed(text.slice(0, displayed.length + 1)),
          typingSpeedMs
        );
        return () => clearTimeout(timeout);
      }
      setPhase("pausing");
      return;
    }

    if (phase === "pausing") {
      const timeout = setTimeout(() => setPhase("deleting"), pauseMs);
      return () => clearTimeout(timeout);
    }

    if (phase === "deleting") {
      if (displayed.length > 0) {
        const timeout = setTimeout(
          () => setDisplayed(text.slice(0, displayed.length - 1)),
          deletingSpeedMs
        );
        return () => clearTimeout(timeout);
      }
      setPhase("typing");
    }
  }, [displayed, phase, text, typingSpeedMs, pauseMs, deletingSpeedMs]);

  return (
    <span>
      {displayed}
      <span className="animate-pulse">|</span>
    </span>
  );
}