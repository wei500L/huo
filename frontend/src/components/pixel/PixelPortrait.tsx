import { memo, useEffect, useMemo, useState } from "react";
import clsx from "clsx";

import {
  PORTRAIT_CATALOG,
  getPortraitSrc,
  type PortraitExpression,
  type PortraitId,
} from "./portraitCatalog";

export interface PixelPortraitProps {
  id: PortraitId;
  expression?: PortraitExpression;
  size?: "sm" | "md" | "lg" | "hero";
  position?: "left" | "right" | "inline";
  bounce?: boolean;
  framed?: boolean;
  className?: string;
}

const SIZE_MAP: Record<NonNullable<PixelPortraitProps["size"]>, { width: number; height: number }> = {
  sm: { width: 96, height: 128 },
  md: { width: 144, height: 192 },
  lg: { width: 192, height: 256 },
  hero: { width: 320, height: 427 },
};

const warned = new Set<string>();

const warnOnce = (message: string): void => {
  if (warned.has(message)) {
    return;
  }

  warned.add(message);
  console.warn(`[PixelPortrait] ${message}`);
};

function PixelPortraitImpl({
  id,
  expression = "neutral",
  size = "md",
  position = "inline",
  bounce = false,
  framed = false,
  className,
}: PixelPortraitProps) {
  const meta = PORTRAIT_CATALOG[id];
  const dimensions = SIZE_MAP[size];
  const [resolvedExpression, setResolvedExpression] = useState<PortraitExpression>(expression);
  const [useNeutralFallback, setUseNeutralFallback] = useState(false);

  useEffect(() => {
    setResolvedExpression(expression);
    setUseNeutralFallback(false);
  }, [expression, id]);

  const src = useMemo(() => {
    const nextExpression = useNeutralFallback ? "neutral" : resolvedExpression;
    return getPortraitSrc(id, nextExpression);
  }, [id, resolvedExpression, useNeutralFallback]);

  const wrapperClassName = clsx(
    "relative shrink-0 overflow-visible pixel-render",
    position === "left" && "absolute bottom-0 left-0",
    position === "right" && "absolute bottom-0 right-0",
    position === "inline" && "inline-block align-bottom",
    bounce && "animate-bounce-pixel",
    framed && "border-2 border-stroke-ink bg-panel shadow-hard",
    className,
  );

  const handleError = () => {
    if (useNeutralFallback || resolvedExpression === "neutral") {
      return;
    }

    warnOnce(`${id}/${resolvedExpression}.png is missing. Falling back to neutral.`);
    setResolvedExpression("neutral");
    setUseNeutralFallback(true);
  };

  const fallbackTone = id === "employee_lin_xiaoman" ? "#7D5AA8" : id === "ceo_female_01" ? "#5B7BE6" : "#6B7280";

  return (
    <div className={wrapperClassName} style={{ width: dimensions.width, height: dimensions.height }}>
      {useNeutralFallback ? (
        <div aria-label={`${meta.id} ${resolvedExpression}`} className="relative h-full w-full overflow-hidden border-2 border-stroke-ink bg-[#F2E7D8] pixel-render">
          <span className="absolute left-[18%] top-[8%] h-[18%] w-[64%] border-2 border-stroke-ink bg-[#F6C8A4]" />
          <span className="absolute left-[12%] top-[2%] h-[22%] w-[76%] border-2 border-stroke-ink" style={{ backgroundColor: fallbackTone }} />
          <span className="absolute left-[28%] top-[18%] h-[8%] w-[10%] bg-ink-1" />
          <span className="absolute right-[28%] top-[18%] h-[8%] w-[10%] bg-ink-1" />
          <span className="absolute left-[24%] top-[32%] h-[8%] w-[52%] border-2 border-stroke-ink bg-[#D98C63]" />
          <span className="absolute left-[20%] top-[42%] h-[26%] w-[60%] border-2 border-stroke-ink bg-[#E9B994]" />
          <span className="absolute left-[16%] top-[56%] h-[26%] w-[68%] border-2 border-stroke-ink" style={{ backgroundColor: fallbackTone }} />
          <span className="absolute left-[10%] bottom-[8%] h-[12%] w-[80%] border-2 border-stroke-ink bg-[#D9D2C2]" />
        </div>
      ) : (
        <img
          alt={`${meta.id} ${useNeutralFallback ? "neutral" : resolvedExpression}`}
          className="block h-full w-full select-none pixel-render"
          height={dimensions.height}
          onError={handleError}
          src={src}
          width={dimensions.width}
        />
      )}
    </div>
  );
}

PixelPortraitImpl.displayName = "PixelPortrait";

export const PixelPortrait = memo(PixelPortraitImpl);
PixelPortrait.displayName = "PixelPortrait";
