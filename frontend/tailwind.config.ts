import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {},
      fontFamily: {
        pixel: ["Fusion Pixel", "monospace"],
        retro: ["Press Start 2P", "monospace"],
      },
      boxShadow: {
        hard: "4px 4px 0 0 #1B1B1B",
      },
    },
  },
  corePlugins: {
    borderRadius: false,
  },
} satisfies Config;
