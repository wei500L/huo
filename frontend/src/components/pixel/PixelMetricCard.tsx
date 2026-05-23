import { forwardRef, type ForwardedRef, type KeyboardEvent } from "react";
import clsx from "clsx";
import { ArrowDown } from "pixelarticons/react/ArrowDown";
import { ArrowUp } from "pixelarticons/react/ArrowUp";

import { useNumberRoll } from "@/anim/numberRoll";

import { PixelIcon } from "./PixelIcon";
import type { IconName } from "./iconCatalog";
import { PixelSparkline } from "./PixelSparkline";

export interface PixelMetricCardProps {
  metricKey: "CASH" | "MORALE" | "BOARD" | "FACE" | "SALES" | "MKT";
  label: string;
  iconName: IconName;
  value: number;
  statusText: string;
  delta?: { value: number; unit?: string };
  sparkline?: number[];
  variant: "blue" | "green" | "orange" | "red" | "purple" | "gold";
  size?: "compact" | "default" | "hero";
  onClick?: () => void;
}

const isMetricV2Enabled = (): boolean => {
  const viteValue = import.meta.env.NEXT_PUBLIC_METRIC_V2;
  if (viteValue) {
    return viteValue === "on";
  }

  if (typeof process !== "undefined") {
    return process.env.NEXT_PUBLIC_METRIC_V2 === "on";
  }

  return false;
};

const shouldRenderMetric = (metricKey: PixelMetricCardProps["metricKey"]): boolean =>
  metricKey !== "SALES" && metricKey !== "MKT" ? true : isMetricV2Enabled();

const TITLE_CLASS: Record<PixelMetricCardProps["variant"], string> = {
  blue: "bg-pixel-blue text-white",
  green: "bg-pixel-green text-white",
  orange: "bg-pixel-orange text-white",
  red: "bg-pixel-red text-white",
  purple: "bg-legacy-purple text-white",
  gold: "bg-exp-gold text-ink-1",
};

const STATUS_CLASS = (text: string): string => {
  if (text.includes("危险")) {
    return "text-pixel-red";
  }
  if (text.includes("健康") || text.includes("稳定") || text.includes("良好")) {
    return "text-pixel-green";
  }
  if (text.includes("中立")) {
    return "text-pixel-orange";
  }
  return "text-ink-2";
};

const SIZE_CLASS: Record<NonNullable<PixelMetricCardProps["size"]>, string> = {
  compact: "min-h-[126px] px-2 py-2",
  default: "min-h-[152px] px-3 py-3",
  hero: "min-h-[176px] px-4 py-4",
};

const VALUE_CLASS: Record<NonNullable<PixelMetricCardProps["size"]>, string> = {
  compact: "text-px-lg",
  default: "text-px-xl",
  hero: "text-px-xxl",
};

const ICON_SIZE: Record<NonNullable<PixelMetricCardProps["size"]>, 24 | 32 | 48> = {
  compact: 24,
  default: 32,
  hero: 48,
};

const ICON_BOX_CLASS: Record<NonNullable<PixelMetricCardProps["size"]>, string> = {
  compact: "h-8 w-8",
  default: "h-10 w-10",
  hero: "h-12 w-12",
};

const SPARK_SIZE: Record<NonNullable<PixelMetricCardProps["size"]>, { width: number; height: number }> = {
  compact: { width: 56, height: 14 },
  default: { width: 60, height: 16 },
  hero: { width: 72, height: 18 },
};

const SPARK_COLOR: Record<PixelMetricCardProps["variant"], string> = {
  blue: "#2E6FE6",
  green: "#3DAE5C",
  orange: "#F39A2B",
  red: "#D9412C",
  purple: "#7B5BE6",
  gold: "#1B1B1B",
};

const formatNumber = (value: number): string =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(value));

function PixelMetricCardImpl(
  { metricKey, label, iconName, value, statusText, delta, sparkline, variant, size = "default", onClick }: PixelMetricCardProps,
  ref: ForwardedRef<HTMLDivElement>,
) {
  const rolledValue = useNumberRoll(value);

  if (!shouldRenderMetric(metricKey)) {
    return null;
  }

  const interactive = Boolean(onClick);
  const deltaPositive = (delta?.value ?? 0) >= 0;
  const deltaTone = deltaPositive ? "text-pixel-green" : "text-pixel-red";
  const sparkSize = SPARK_SIZE[size];

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
    <div
      ref={ref}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      className={clsx(
        "relative flex flex-col overflow-hidden border-2 border-stroke-ink bg-panel text-ink-1 shadow-hard pixel-render",
        interactive && "cursor-pointer",
        SIZE_CLASS[size],
      )}
    >
      <div className={clsx("flex h-8 items-center justify-center border-b-2 border-stroke-ink px-2 text-px-sm leading-none", TITLE_CLASS[variant])}>
        <span className="min-w-0 truncate text-center">{label}</span>
      </div>

      <div className="flex flex-1 flex-col gap-2">
        <div className="flex items-center gap-2 pt-2">
          <div className={clsx("flex shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim", ICON_BOX_CLASS[size])}>
            <PixelIcon name={iconName} size={ICON_SIZE[size]} ariaLabel={label} />
          </div>

          <div className="min-w-0 flex-1">
            <div className={clsx("font-retro leading-none text-ink-1", VALUE_CLASS[size])}>{formatNumber(rolledValue)}</div>
            <div className={clsx("mt-1 text-px-sm leading-none", STATUS_CLASS(statusText))}>{statusText}</div>
          </div>
        </div>

        <div className="mt-auto flex items-end justify-between gap-2">
          <div className="shrink-0">
            {sparkline?.length ? <PixelSparkline values={sparkline} color={SPARK_COLOR[variant]} width={sparkSize.width} height={sparkSize.height} /> : null}
          </div>

          {delta ? (
            <div className={clsx("flex shrink-0 items-center gap-1 text-px-sm leading-none", deltaTone)}>
              {deltaPositive ? <ArrowUp aria-hidden="true" className="h-4 w-4" /> : <ArrowDown aria-hidden="true" className="h-4 w-4" />}
              <span>
                {deltaPositive ? "+" : "-"}
                {formatNumber(Math.abs(delta.value))}
                {delta.unit ? ` ${delta.unit}` : ""}
              </span>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

PixelMetricCardImpl.displayName = "PixelMetricCard";

export const PixelMetricCard = forwardRef(PixelMetricCardImpl);
