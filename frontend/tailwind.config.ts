import type { Config } from "tailwindcss";

// Design tokens kept centralized here so every feature (editor, timeline,
// complexity graph, etc.) draws from the same palette instead of hardcoding
// hex values inline — this is what keeps a dark/glassmorphism UI coherent
// as the app grows past a handful of components.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        surface: "rgba(255, 255, 255, 0.04)",
        border: "rgba(255, 255, 255, 0.08)",
        primary: {
          DEFAULT: "#7C3AED",
          light: "#A78BFA",
        },
        accent: "#22D3EE",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
} satisfies Config;
