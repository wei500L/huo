export const SPACING = {
  xs: 4,
  sm: 8,
  md: 12,
  base: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const RADIUS = {
  none: 0,
  step: 2,
} as const;

export const FONT_SIZE = {
  xs: 10,
  sm: 12,
  base: 12,
  md: 16,
  lg: 20,
  xl: 24,
  xxl: 32,
  hero: 48,
} as const;

export const LINE_HEIGHT = {
  tight: 1.2,
  normal: 1.4,
  loose: 1.6,
} as const;

export const SHADOW = {
  hard: "4px 4px 0 0 #1B1B1B",
  hardSm: "2px 2px 0 0 #1B1B1B",
  hardLg: "6px 6px 0 0 #1B1B1B",
  innerHard: "inset 2px 2px 0 0 #1B1B1B",
} as const;

export const BORDER = {
  thin: 1,
  pixel: 2,
  bold: 4,
} as const;

export const Z_INDEX = {
  hud: 100,
  mainBar: 100,
  dialog: 200,
  toast: 300,
  overlay: 400,
} as const;

export const ANIM = {
  typewriterMsPerChar: 30,
  numberRollMs: 400,
  pulseHz: 0.6,
  toastMs: 3000,
  cardEnterMs: 200,
} as const;
