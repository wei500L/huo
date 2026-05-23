import type { Config } from "tailwindcss";

import {
  ANIM,
  BORDER,
  FONT_SIZE,
  LINE_HEIGHT,
  PALETTE,
  SHADOW,
  SPACING,
  Z_INDEX,
} from "./src/theme";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  safelist: [
    "bg-pixel-blue",
    "border-stroke-ink",
    "font-pixel",
    "shadow-hard",
    "text-px-base",
  ],
  corePlugins: {
    preflight: true,
    borderRadius: false,
  },
  theme: {
    borderRadius: {
      none: "0",
      step: "2px",
    },
    extend: {
      fontFamily: {
        pixel: ['"Fusion Pixel"', "monospace"],
        retro: ['"Press Start 2P"', "monospace"],
      },
      colors: {
        canvas: PALETTE.bg.canvas,
        panel: PALETTE.bg.panel,
        "panel-dim": PALETTE.bg.panelDim,
        floor: PALETTE.bg.floor,
        "ink-1": PALETTE.ink.primary,
        "ink-2": PALETTE.ink.secondary,
        "ink-3": PALETTE.ink.muted,
        "pixel-blue": PALETTE.brand.blue,
        "pixel-green": PALETTE.brand.green,
        "pixel-orange": PALETTE.brand.orange,
        "pixel-red": PALETTE.brand.red,
        "alarm-red": PALETTE.alarm.red,
        "caution-yellow": PALETTE.alarm.yellow,
        "exp-gold": PALETTE.game.expGold,
        "legacy-purple": PALETTE.game.legacyPurple,
        "stroke-ink": PALETTE.stroke.ink,
      },
      fontSize: {
        "px-xs": [`${FONT_SIZE.xs}px`, `${LINE_HEIGHT.tight}`],
        "px-sm": [`${FONT_SIZE.sm}px`, `${LINE_HEIGHT.normal}`],
        "px-base": [`${FONT_SIZE.base}px`, `${LINE_HEIGHT.normal}`],
        "px-md": [`${FONT_SIZE.md}px`, `${LINE_HEIGHT.normal}`],
        "px-lg": [`${FONT_SIZE.lg}px`, `${LINE_HEIGHT.tight}`],
        "px-xl": [`${FONT_SIZE.xl}px`, `${LINE_HEIGHT.tight}`],
        "px-xxl": [`${FONT_SIZE.xxl}px`, `${LINE_HEIGHT.tight}`],
        "px-hero": [`${FONT_SIZE.hero}px`, `${LINE_HEIGHT.tight}`],
      },
      spacing: {
        "px-xs": `${SPACING.xs}px`,
        "px-sm": `${SPACING.sm}px`,
        "px-md": `${SPACING.md}px`,
        "px-base": `${SPACING.base}px`,
        "px-lg": `${SPACING.lg}px`,
        "px-xl": `${SPACING.xl}px`,
        "px-xxl": `${SPACING.xxl}px`,
      },
      borderWidth: {
        thin: `${BORDER.thin}px`,
        pixel: `${BORDER.pixel}px`,
        bold: `${BORDER.bold}px`,
      },
      boxShadow: {
        hard: SHADOW.hard,
        "hard-sm": SHADOW.hardSm,
        "hard-lg": SHADOW.hardLg,
        "inner-hard": SHADOW.innerHard,
      },
      lineHeight: {
        tight: `${LINE_HEIGHT.tight}`,
        normal: `${LINE_HEIGHT.normal}`,
        loose: `${LINE_HEIGHT.loose}`,
      },
      zIndex: {
        hud: `${Z_INDEX.hud}`,
        mainBar: `${Z_INDEX.mainBar}`,
        dialog: `${Z_INDEX.dialog}`,
        toast: `${Z_INDEX.toast}`,
        overlay: `${Z_INDEX.overlay}`,
      },
      animation: {
        pulseAlarm: `pulseAlarm ${1 / ANIM.pulseHz}s ease-in-out infinite`,
        typewriter: `typewriter ${ANIM.typewriterMsPerChar * 40}ms steps(40) forwards`,
      },
      keyframes: {
        pulseAlarm: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.6" },
        },
        typewriter: {
          from: { width: "0" },
          to: { width: "100%" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
