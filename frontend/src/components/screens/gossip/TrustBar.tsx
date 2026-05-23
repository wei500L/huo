import clsx from "clsx";

import { PixelIcon } from "@/components/pixel";

export interface TrustBarProps {
  value: number;
  label?: string;
  size?: "sm" | "md";
}

type TrustBucket = "friendly" | "neutral" | "hostile" | "broken";

const BUCKET_META: Record<
  TrustBucket,
  { label: string; rootClass: string; fillClass: string; textClass: string }
> = {
  friendly: {
    label: "友好",
    rootClass: "bg-[#E8F5EA]",
    fillClass: "bg-pixel-green",
    textClass: "text-pixel-green",
  },
  neutral: {
    label: "中立",
    rootClass: "bg-[#EEF0F2]",
    fillClass: "bg-ink-3",
    textClass: "text-ink-2",
  },
  hostile: {
    label: "敌意",
    rootClass: "bg-[#FFF1E1]",
    fillClass: "bg-pixel-orange",
    textClass: "text-pixel-orange",
  },
  broken: {
    label: "崩坏",
    rootClass: "bg-[#FFF0EE]",
    fillClass: "bg-pixel-red",
    textClass: "text-pixel-red",
  },
};

const clampTrust = (value: number): number => {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.min(100, Math.max(0, Math.trunc(value)));
};

const getBucket = (value: number): TrustBucket => {
  if (value >= 70) {
    return "friendly";
  }

  if (value >= 30) {
    return "neutral";
  }

  if (value >= 10) {
    return "hostile";
  }

  return "broken";
};

export function TrustBar({ value, label, size = "md" }: TrustBarProps) {
  const normalizedValue = clampTrust(value);
  const meta = BUCKET_META[getBucket(normalizedValue)];

  return (
    <div
      className={clsx(
        "border-2 border-stroke-ink shadow-hard-sm",
        meta.rootClass,
        size === "sm" ? "px-px-sm py-px-xs" : "px-px-md py-px-sm",
      )}
    >
      <div className="mb-px-xs flex items-center gap-px-sm">
        <PixelIcon ariaLabel="trust" name="morale" size={size === "sm" ? 16 : 24} />
        <span className={clsx("font-pixel leading-none", size === "sm" ? "text-px-sm" : "text-px-md")}>
          信任度 {normalizedValue}
        </span>
        <span className={clsx("ml-auto font-pixel leading-none", meta.textClass)}>
          {label ?? meta.label}
        </span>
      </div>
      <div className="h-3 border-2 border-stroke-ink bg-panel">
        <div className={clsx("h-full", meta.fillClass)} style={{ width: `${normalizedValue}%` }} />
      </div>
    </div>
  );
}
