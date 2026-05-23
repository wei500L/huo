import { describe, expect, it } from "vitest";

import { ANIM, FONT_SIZE, PALETTE, SHADOW, SPACING } from "@/theme";

type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends <
  T,
>() => T extends B ? 1 : 2
  ? true
  : false;

type Expect<T extends true> = T;

type ExpectedPalette = {
  readonly bg: {
    readonly canvas: "#F4F2EB";
    readonly panel: "#FFFFFF";
    readonly panelDim: "#ECE9DF";
    readonly floor: "#DCD7C7";
  };
  readonly ink: {
    readonly primary: "#1B1B1B";
    readonly secondary: "#4A4A4A";
    readonly muted: "#8C8C8C";
  };
  readonly brand: {
    readonly blue: "#2E6FE6";
    readonly green: "#3DAE5C";
    readonly orange: "#F39A2B";
    readonly red: "#D9412C";
  };
  readonly alarm: {
    readonly red: "#E63946";
    readonly yellow: "#F5C518";
  };
  readonly game: {
    readonly expGold: "#FFD23F";
    readonly legacyPurple: "#7B5BE6";
  };
  readonly stroke: {
    readonly ink: "#1B1B1B";
  };
};

type ExpectedSpacing = {
  readonly xs: 4;
  readonly sm: 8;
  readonly md: 12;
  readonly base: 16;
  readonly lg: 24;
  readonly xl: 32;
  readonly xxl: 48;
};

type ExpectedFontSize = {
  readonly xs: 10;
  readonly sm: 12;
  readonly base: 12;
  readonly md: 16;
  readonly lg: 20;
  readonly xl: 24;
  readonly xxl: 32;
  readonly hero: 48;
};

type _paletteFrozen = Expect<Equal<typeof PALETTE, ExpectedPalette>>;
type _spacingFrozen = Expect<Equal<typeof SPACING, ExpectedSpacing>>;
type _fontSizeFrozen = Expect<Equal<typeof FONT_SIZE, ExpectedFontSize>>;

describe("theme tokens", () => {
  it("matches the pixel palette", () => {
    expect(PALETTE.bg.canvas).toBe("#F4F2EB");
    expect(PALETTE.bg.panel).toBe("#FFFFFF");
    expect(PALETTE.bg.panelDim).toBe("#ECE9DF");
    expect(PALETTE.bg.floor).toBe("#DCD7C7");
    expect(PALETTE.ink.primary).toBe("#1B1B1B");
    expect(PALETTE.ink.secondary).toBe("#4A4A4A");
    expect(PALETTE.ink.muted).toBe("#8C8C8C");
    expect(PALETTE.brand.blue).toBe("#2E6FE6");
    expect(PALETTE.brand.green).toBe("#3DAE5C");
    expect(PALETTE.brand.orange).toBe("#F39A2B");
    expect(PALETTE.brand.red).toBe("#D9412C");
    expect(PALETTE.alarm.red).toBe("#E63946");
    expect(PALETTE.alarm.yellow).toBe("#F5C518");
    expect(PALETTE.game.expGold).toBe("#FFD23F");
    expect(PALETTE.game.legacyPurple).toBe("#7B5BE6");
    expect(PALETTE.stroke.ink).toBe("#1B1B1B");
  });

  it("keeps hard shadows and timing constants", () => {
    expect(SHADOW.hard).toContain("0 0 #1B1B1B");
    expect(ANIM.typewriterMsPerChar).toBe(30);
  });
});
