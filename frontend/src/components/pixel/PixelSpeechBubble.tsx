import { memo, useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import { ChevronDown } from "pixelarticons/react/ChevronDown";

import { useTypewriter } from "@/anim/typewriter";

import { PixelIcon } from "./PixelIcon";

type TrustBucket = "green" | "gray" | "orange";

export interface PixelSpeechBubbleProps {
  speaker?: { name: string; role?: string };
  text: string;
  typewriter?: boolean;
  typewriterSpeedMs?: number;
  trust?: { value: number; label: string };
  tone?: "friendly" | "neutral" | "hostile" | "thinking" | "rip";
  arrow?: "left" | "right" | "down" | "none";
  collapsible?: boolean;
  onComplete?: () => void;
  className?: string;
}

const TONE_SURFACE: Record<NonNullable<PixelSpeechBubbleProps["tone"]>, string> = {
  friendly: "var(--color-panel)",
  neutral: "#FBFBF8",
  hostile: "#FFF5F5",
  thinking: "#F5F7FB",
  rip: "#F8F3F3",
};

const TRUST_STYLE: Record<TrustBucket, { backgroundColor: string; color: string; label: string }> = {
  green: { backgroundColor: "#E8F5EA", color: "#3DAE5C", label: "友好" },
  gray: { backgroundColor: "#EEF0F2", color: "#4A4A4A", label: "中立" },
  orange: { backgroundColor: "#FFF1E1", color: "#F39A2B", label: "敌意" },
};

const warnedTrustValues = new Set<number>();

const normalizeTrust = (value: number): number => {
  if (value < 0 || value > 100) {
    if (!warnedTrustValues.has(value)) {
      warnedTrustValues.add(value);
      console.warn(`[PixelSpeechBubble] trust value ${value} is out of range 0-100. Clamping.`);
    }
  }

  return Math.min(100, Math.max(0, value));
};

const getTrustBucket = (value: number): TrustBucket => {
  if (value >= 70) {
    return "green";
  }

  if (value >= 30) {
    return "gray";
  }

  return "orange";
};

function PixelSpeechBubbleImpl({
  speaker,
  text,
  typewriter = false,
  typewriterSpeedMs = 30,
  trust,
  tone = "friendly",
  arrow = "none",
  collapsible = false,
  onComplete,
  className,
}: PixelSpeechBubbleProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { display, isDone, skip } = useTypewriter(text, typewriter, typewriterSpeedMs);
  const completedTextRef = useRef<string | null>(null);

  const surfaceColor = TONE_SURFACE[tone];
  const trustMeta = useMemo(() => {
    if (!trust) {
      return null;
    }

    const normalizedValue = normalizeTrust(trust.value);
    const bucket = getTrustBucket(normalizedValue);

    return {
      value: normalizedValue,
      bucket,
      label: TRUST_STYLE[bucket].label,
      style: TRUST_STYLE[bucket],
    };
  }, [trust]);

  useEffect(() => {
    if (!typewriter) {
      completedTextRef.current = text;
      return;
    }

    if (isDone && completedTextRef.current !== text) {
      completedTextRef.current = text;
      onComplete?.();
    }

    if (!isDone) {
      completedTextRef.current = null;
    }
  }, [isDone, onComplete, text, typewriter]);

  useEffect(() => {
    if (!typewriter || isDone) {
      return;
    }

    const handleKeyDown = () => {
      skip();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isDone, skip, typewriter]);

  const arrowStyle = useMemo(() => {
    if (arrow === "none") {
      return null;
    }

    const borderSize = 6;
    const color = surfaceColor;

    if (arrow === "down") {
      return {
        borderLeft: `${borderSize}px solid transparent`,
        borderRight: `${borderSize}px solid transparent`,
        borderTop: `${borderSize}px solid ${color}`,
        bottom: `-${borderSize}px`,
        left: "50%",
        transform: "translateX(-50%)",
      } as const;
    }

    if (arrow === "left") {
      return {
        borderTop: `${borderSize}px solid transparent`,
        borderBottom: `${borderSize}px solid transparent`,
        borderRight: `${borderSize}px solid ${color}`,
        left: `-${borderSize}px`,
        top: "24px",
      } as const;
    }

    return {
      borderTop: `${borderSize}px solid transparent`,
      borderBottom: `${borderSize}px solid transparent`,
      borderLeft: `${borderSize}px solid ${color}`,
      right: `-${borderSize}px`,
      top: "24px",
    } as const;
  }, [arrow, surfaceColor]);

  const rootClassName = clsx(
    "relative w-full min-w-0 border-2 border-stroke-ink shadow-hard font-pixel",
    tone === "hostile" && "bg-[#FFF5F5]",
    tone === "thinking" && "bg-[#F5F7FB]",
    tone === "rip" && "bg-[#F8F3F3]",
    tone === "neutral" && "bg-[#FBFBF8]",
    tone === "friendly" && "bg-panel",
    className,
  );

  return (
    <section className={rootClassName} style={{ backgroundColor: surfaceColor }}>
      {collapsible ? (
        <button
          aria-label={collapsed ? "展开对话" : "折叠对话"}
          aria-expanded={!collapsed}
          className="absolute right-1 top-1 flex h-5 w-5 items-center justify-center border border-stroke-ink bg-panel text-ink-1"
          type="button"
          onClick={() => setCollapsed((value) => !value)}
        >
          <ChevronDown className={clsx("h-3 w-3", collapsed && "rotate-180")} />
        </button>
      ) : null}

      {speaker ? (
        <div className="border-b-2 border-stroke-ink bg-ink-1 px-px-md py-px-xs text-px-sm text-white">
          <span className="block break-words leading-tight">
            {speaker.name}
            {speaker.role ? ` | ${speaker.role}` : ""}
          </span>
        </div>
      ) : null}

      {!collapsed ? (
        <div className={clsx("relative px-px-md py-px-md text-ink-1", trustMeta && "pb-px-xl")}>
          <p className="break-words whitespace-pre-wrap text-px-md leading-[1.4]">
            {display}
            {typewriter && !isDone ? (
              <span aria-hidden="true" className="animate-cursor-blink">
                _
              </span>
            ) : null}
          </p>

          {trustMeta ? (
            <div
              className="absolute bottom-px-md left-px-md inline-flex items-center gap-1 border border-stroke-ink px-2 py-1 text-px-sm"
              style={{ backgroundColor: trustMeta.style.backgroundColor, color: trustMeta.style.color }}
            >
              <PixelIcon ariaLabel="trust" name="morale" size={16} />
              <span>{`信任度 ${trustMeta.value}`}</span>
              <span>{trustMeta.label}</span>
            </div>
          ) : null}
        </div>
      ) : null}

      {arrow !== "none" ? (
        <span aria-hidden="true" className="absolute block h-0 w-0" style={arrowStyle ?? undefined} />
      ) : null}
    </section>
  );
}

PixelSpeechBubbleImpl.displayName = "PixelSpeechBubble";

export const PixelSpeechBubble = memo(PixelSpeechBubbleImpl);
PixelSpeechBubble.displayName = "PixelSpeechBubble";
