import clsx from "clsx";

import { PixelCard, PixelIcon, type IconName } from "@/components/pixel";
import type { DecisionCardDTO, StatsDTO } from "@/protocol/types";

interface Props {
  card?: DecisionCardDTO | null;
}

type MetricKey = keyof StatsDTO;

const METRICS: Array<{ key: MetricKey; icon: IconName; label: string }> = [
  { key: "CASH", icon: "money", label: "现金流" },
  { key: "MORALE", icon: "morale", label: "士气" },
  { key: "BOARD", icon: "board", label: "信任" },
  { key: "FACE", icon: "face", label: "体面" },
];

const formatDelta = (key: MetricKey, value = 0): string => {
  const sign = value > 0 ? "+" : "";
  if (key === "CASH") {
    return `${sign}${value >= 0 ? "¥" : "-¥"}${Math.abs(value).toLocaleString("zh-CN")}`;
  }

  return `${sign}${value}`;
};

export const EffectPreview = ({ card }: Props) => {
  if (!card) {
    return null;
  }

  return (
    <PixelCard className="w-[240px] shadow-hard-lg" kind="info" title="预计即时变化" titleColor="blue">
      <div className="grid h-[76px] grid-cols-2 gap-x-px-md gap-y-px-sm">
        {METRICS.map((metric) => {
          const value = card.immediateEffect[metric.key] ?? 0;

          return (
            <div key={metric.key} className="flex min-w-0 items-center gap-px-xs">
              <PixelIcon name={metric.icon} size={16} />
              <span className="min-w-0 flex-1 truncate text-px-xs text-ink-2">{metric.label}</span>
              <span className={clsx("font-retro text-[9px]", value >= 0 ? "text-pixel-green" : "text-pixel-red")}>
                {formatDelta(metric.key, value)}
              </span>
            </div>
          );
        })}
      </div>
    </PixelCard>
  );
};
