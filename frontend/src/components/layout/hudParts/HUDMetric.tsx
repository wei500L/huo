import clsx from "clsx";

import { PixelIcon, type IconName } from "@/components/pixel";

export interface HUDMetricProps {
  icon: IconName;
  label: string;
  value: string;
  delta?: string;
  status?: string;
  unit?: string;
  variant: "blue" | "green" | "orange" | "red" | "purple" | "gold";
  dimmed?: boolean;
}

const VARIANT_BADGE: Record<HUDMetricProps["variant"], string> = {
  blue: "bg-pixel-blue text-white",
  green: "bg-pixel-green text-white",
  orange: "bg-pixel-orange text-white",
  red: "bg-pixel-red text-white",
  purple: "bg-legacy-purple text-white",
  gold: "bg-exp-gold text-ink-1",
};

const VARIANT_VALUE: Record<HUDMetricProps["variant"], string> = {
  blue: "text-pixel-blue",
  green: "text-pixel-green",
  orange: "text-pixel-orange",
  red: "text-pixel-red",
  purple: "text-legacy-purple",
  gold: "text-ink-1",
};

const parseNumericValue = (input: string): number | null => {
  if (input.length === 0 || /^v\d+$/i.test(input)) {
    return null;
  }

  const normalized = input.replace(/[^0-9.-]/g, "");
  if (normalized.length === 0) {
    return null;
  }

  const parsed = Number.parseFloat(normalized);
  return Number.isFinite(parsed) ? parsed : null;
};

const resolveDeltaClass = (delta?: string): string => {
  if (!delta) {
    return "text-ink-2";
  }

  const sign = delta.trim()[0];
  if (sign === "+") {
    return "text-pixel-green";
  }

  if (sign === "-") {
    return "text-pixel-red";
  }

  return "text-ink-2";
};

const resolveStatus = (label: string, value: string): string | undefined => {
  const numericValue = parseNumericValue(value);
  if (numericValue === null) {
    return undefined;
  }

  const normalizedLabel = label.toUpperCase();
  if (normalizedLabel.includes("现金") || normalizedLabel === "CASH") {
    return numericValue <= 5 ? "中立" : numericValue >= 60 ? "健康" : "稳定";
  }

  if (normalizedLabel.includes("士气") || normalizedLabel === "MORALE") {
    return numericValue >= 60 ? "健康" : numericValue >= 35 ? "稳定" : "中立";
  }

  if (normalizedLabel.includes("董事") || normalizedLabel === "BOARD") {
    return numericValue >= 55 ? "健康" : numericValue >= 35 ? "稳定" : "中立";
  }

  if (normalizedLabel.includes("面子") || normalizedLabel === "FACE") {
    return numericValue >= 45 ? "健康" : numericValue >= 25 ? "稳定" : "中立";
  }

  return undefined;
};

const isCrisisMetric = (label: string, value: string): boolean => {
  const normalizedLabel = label.toUpperCase();
  if (!(normalizedLabel.includes("现金") || normalizedLabel === "CASH")) {
    return false;
  }

  const numericValue = parseNumericValue(value);
  return numericValue !== null && numericValue <= 5;
};

export const HUDMetric = ({ icon, label, value, delta, status, unit, variant, dimmed = false }: HUDMetricProps) => {
  const resolvedStatus = status ?? resolveStatus(label, value);
  const crisis = isCrisisMetric(label, value);
  const deltaClass = resolveDeltaClass(delta);

  return (
    <article
      data-dimmed={dimmed ? "true" : "false"}
      data-variant={variant}
      className={clsx(
        "flex h-14 min-w-[96px] max-w-[132px] flex-1 overflow-hidden border-2 border-stroke-ink shadow-hard",
        dimmed ? "bg-panel-dim opacity-50" : "bg-panel",
        crisis && "animate-pulse bg-alarm-red text-white",
      )}
    >
      <div className="flex h-full min-w-0 flex-1 flex-col justify-between px-2 py-1">
        <div className="flex min-w-0 items-center gap-1">
          <span
            aria-hidden="true"
            className={clsx(
              "flex h-5 w-5 shrink-0 items-center justify-center border border-stroke-ink",
              crisis ? "bg-white text-alarm-red" : VARIANT_BADGE[variant],
            )}
          >
            <PixelIcon name={icon} size={16} />
          </span>

          <span className={clsx("min-w-0 truncate text-[10px] leading-none", crisis ? "text-white" : "text-ink-1")}>
            {label}
          </span>

          {resolvedStatus ? (
            <span
              className={clsx(
                "ml-auto shrink-0 border border-stroke-ink px-1 text-[10px] leading-none",
                crisis ? "bg-white text-alarm-red" : "bg-panel-dim text-ink-1",
              )}
            >
              {resolvedStatus}
            </span>
          ) : null}
        </div>

        <div className="flex min-w-0 items-end gap-1">
          <span
            className={clsx(
              "min-w-0 truncate font-retro text-[13px] leading-none",
              crisis ? "text-white" : VARIANT_VALUE[variant],
            )}
          >
            {value}
          </span>
          {unit ? (
            <span className={clsx("shrink-0 text-[10px] leading-none", crisis ? "text-white" : "text-ink-2")}>
              {unit}
            </span>
          ) : null}
        </div>

        <div className="flex min-w-0 items-center justify-between gap-1">
          {delta ? (
            <span className={clsx("truncate text-[10px] leading-none", crisis ? "text-white" : deltaClass)}>
              {delta}
            </span>
          ) : (
            <span className="text-[10px] leading-none text-transparent">-</span>
          )}
        </div>
      </div>
    </article>
  );
};
