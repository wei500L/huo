import { forwardRef, type KeyboardEvent, type ReactNode } from "react";
import clsx from "clsx";
import { Check } from "pixelarticons/react/Check";

import { Card as EightBitCard } from "@/components/ui/8bit";
import type { Variant } from "./PixelButton";

export type CardKind = "default" | "metric" | "decision" | "risk" | "info" | "event";

export interface PixelCardProps {
  kind?: CardKind;
  title?: string;
  titleColor?: Variant;
  badge?: ReactNode;
  footer?: ReactNode;
  selected?: boolean;
  dimmed?: boolean;
  onClick?: () => void;
  className?: string;
  children: ReactNode;
}

const KIND_TO_VARIANT: Record<Exclude<CardKind, "default">, Variant> = {
  metric: "blue",
  decision: "orange",
  risk: "red",
  info: "green",
  event: "ghost",
};

const TITLE_CLASS: Record<Variant, string> = {
  blue: "bg-pixel-blue text-white",
  green: "bg-pixel-green text-white",
  purple: "bg-legacy-purple text-white",
  orange: "bg-pixel-orange text-white",
  red: "bg-pixel-red text-white",
  danger: "bg-alarm-red text-white",
  ghost: "bg-panel-dim text-ink-1",
};

export const PixelCard = forwardRef<HTMLDivElement, PixelCardProps>(
  (
    { kind = "default", title, titleColor, badge, footer, selected = false, dimmed = false, onClick, className, children },
    ref,
  ) => {
    const resolvedColor = titleColor ?? (kind === "default" ? undefined : KIND_TO_VARIANT[kind]);
    const interactive = Boolean(onClick);

    const handleClick = interactive ? () => onClick?.() : undefined;

    const handleKeyDown = interactive
      ? (event: KeyboardEvent<HTMLDivElement>) => {
          if (event.target !== event.currentTarget) {
            return;
          }

          if (event.key !== "Enter" && event.key !== " ") {
            return;
          }

          event.preventDefault();
          onClick?.();
        }
      : undefined;

    return (
      <EightBitCard
        ref={ref}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role={interactive ? "button" : undefined}
        tabIndex={interactive ? 0 : undefined}
        className={clsx(
          "relative border-2 border-stroke-ink bg-panel shadow-hard overflow-hidden text-ink-1",
          selected && "outline outline-2 outline-exp-gold shadow-[6px_6px_0_0_var(--stroke-ink)]",
          interactive && "cursor-pointer",
          className,
        )}
        style={dimmed ? { filter: "grayscale(0.6)", opacity: 0.7 } : undefined}
      >
        {title || badge || resolvedColor ? (
          <div
            className={clsx(
              "flex h-8 items-center border-b-2 border-stroke-ink px-px-md text-px-sm leading-none",
              resolvedColor ? TITLE_CLASS[resolvedColor] : "bg-transparent text-ink-1",
            )}
          >
            <div className="min-w-0 flex-1 truncate">{title ?? ""}</div>
            {badge ? <div className="ml-px-sm shrink-0">{badge}</div> : null}
          </div>
        ) : null}

        <div className="px-px-md py-px-md">{children}</div>

        {footer ? <div className="border-t-2 border-stroke-ink px-px-md py-px-sm">{footer}</div> : null}

        {selected ? (
          <span aria-hidden="true" className="absolute right-0 top-0 flex h-6 w-6 items-center justify-center border-b-2 border-l-2 border-stroke-ink bg-exp-gold">
            <Check className="h-4 w-4" />
          </span>
        ) : null}
      </EightBitCard>
    );
  },
);

PixelCard.displayName = "PixelCard";
