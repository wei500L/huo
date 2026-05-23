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

  return (
    <div className={wrapperClassName} style={{ width: dimensions.width, height: dimensions.height }}>
      <img
        alt={`${meta.id} ${useNeutralFallback ? "neutral" : resolvedExpression}`}
        className="block h-full w-full select-none pixel-render"
        height={dimensions.height}
        onError={handleError}
        src={src}
        width={dimensions.width}
      />
    </div>
  );
}

PixelPortraitImpl.displayName = "PixelPortrait";

export const PixelPortrait = memo(PixelPortraitImpl);
PixelPortrait.displayName = "PixelPortrait";
