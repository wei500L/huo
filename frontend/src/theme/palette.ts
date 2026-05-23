export const PALETTE = {
  bg: {
    canvas: "#F4F2EB",
    panel: "#FFFFFF",
    panelDim: "#ECE9DF",
    floor: "#DCD7C7",
  },
  ink: {
    primary: "#1B1B1B",
    secondary: "#4A4A4A",
    muted: "#8C8C8C",
  },
  brand: {
    blue: "#2E6FE6",
    green: "#3DAE5C",
    orange: "#F39A2B",
    red: "#D9412C",
  },
  alarm: {
    red: "#E63946",
    yellow: "#F5C518",
  },
  game: {
    expGold: "#FFD23F",
    legacyPurple: "#7B5BE6",
  },
  stroke: {
    ink: "#1B1B1B",
  },
} as const;

export type PaletteToken = typeof PALETTE;
