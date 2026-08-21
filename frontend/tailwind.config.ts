import type { Config } from "tailwindcss";

// Design tokens drawn from the Psychic/Dark Pokémon reference set:
// near-black base, with three glow accents (amber, magenta, toxic-green)
// used sparingly as focal points -- never as flat fills.
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#050507",
        surface: "rgba(255, 255, 255, 0.04)",
        border: "rgba(255, 255, 255, 0.08)",
        primary: {
          DEFAULT: "#F5A623",
          light: "#FFC978",
          dark: "#B36E00",
        },
        accent: {
          DEFAULT: "#FF2E7E",
          light: "#FF6FA8",
        },
        toxic: {
          DEFAULT: "#39FF88",
          light: "#8CFFC0",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Alex Brush", "cursive"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        "glow-amber": "0 0 40px 4px rgba(245, 166, 35, 0.35)",
        "glow-magenta": "0 0 40px 4px rgba(255, 46, 126, 0.35)",
        "glow-toxic": "0 0 40px 4px rgba(57, 255, 136, 0.3)",
      },
      backdropBlur: {
        xs: "2px",
      },
    },
  },
  plugins: [],
} satisfies Config;