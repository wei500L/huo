import { PixelIcon } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import {
  selectCurrentQuarter,
  selectCurrentSnapshot,
  selectCurrentStats,
  selectHistory,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { DateCard, HUDMetric, LogoBadge } from "./hudParts";

const formatDelta = (current?: number, previous?: number): string | undefined => {
  if (!Number.isFinite(current ?? NaN) || !Number.isFinite(previous ?? NaN)) {
    return undefined;
  }

  const delta = (current as number) - (previous as number);
  if (delta === 0) {
    return undefined;
  }

  const sign = delta > 0 ? "+" : "";
  return `${sign}${Math.abs(delta).toLocaleString("en-US")}`;
};

const formatMetricValue = (key: "cash" | "morale" | "board" | "face", value?: number): string => {
  if (!Number.isFinite(value ?? NaN)) {
    return "-/-";
  }

  const formatted = Math.trunc(value as number).toLocaleString("en-US");
  return key === "cash" ? `¥${formatted}` : formatted;
};

const formatStatStatus = (key: "cash" | "morale" | "board" | "face", value?: number): string | undefined => {
  if (!Number.isFinite(value ?? NaN)) {
    return undefined;
  }

  const resolved = value as number;
  switch (key) {
    case "cash":
      return resolved <= 5 ? "中立" : resolved >= 60 ? "健康" : "稳定";
    case "morale":
      return resolved >= 60 ? "健康" : resolved >= 35 ? "稳定" : "中立";
    case "board":
      return resolved >= 55 ? "健康" : resolved >= 35 ? "稳定" : "中立";
    case "face":
      return resolved >= 45 ? "健康" : resolved >= 25 ? "稳定" : "中立";
    default:
      return undefined;
  }
};

export const HUDBar = () => {
  const snapshot = useGameStore(selectCurrentSnapshot);
  const stats = useGameStore(selectCurrentStats);
  const quarter = useGameStore(selectCurrentQuarter);
  const history = useGameStore(selectHistory);
  const push = useScreenStore((state) => state.push);
  const latestHistory = history[history.length - 1] ?? null;
  const previousStats = latestHistory?.statsBefore ?? null;

  const quarterNumber = quarter?.number ?? 0;
  const coreMetrics = [
    {
      icon: "money" as const,
      label: "现金流",
      value: formatMetricValue("cash", stats?.cash),
      delta: formatDelta(stats?.cash, previousStats?.cash),
      status: formatStatStatus("cash", stats?.cash),
      variant: "gold" as const,
    },
    {
      icon: "morale" as const,
      label: "士气",
      value: formatMetricValue("morale", stats?.morale),
      delta: formatDelta(stats?.morale, previousStats?.morale),
      status: formatStatStatus("morale", stats?.morale),
      variant: "green" as const,
    },
    {
      icon: "board" as const,
      label: "董事会",
      value: formatMetricValue("board", stats?.board),
      delta: formatDelta(stats?.board, previousStats?.board),
      status: formatStatStatus("board", stats?.board),
      variant: "blue" as const,
    },
    {
      icon: "face" as const,
      label: "面子",
      value: formatMetricValue("face", stats?.face),
      delta: formatDelta(stats?.face, previousStats?.face),
      status: formatStatStatus("face", stats?.face),
      variant: "purple" as const,
    },
  ];

  return (
    <header className="flex flex-col gap-3 overflow-x-hidden overflow-y-visible border-b-2 border-stroke-ink bg-panel px-3 py-3 sm:px-4 lg:h-20 lg:flex-row lg:items-center lg:py-0">
      <span className="sr-only">HUD</span>

      <LogoBadge />

      <DateCard
        day={quarterNumber}
        time="--:--"
        weekday={quarter?.phase ?? "--"}
        date={snapshot?.company.name ?? "--"}
      />

      <div className="flex min-w-0 flex-1 flex-wrap items-stretch gap-2 overflow-hidden">
        {coreMetrics.map((metric) => (
          <div key={metric.label} className="min-w-0 flex-1">
            <HUDMetric
              icon={metric.icon}
              label={metric.label}
              value={metric.value}
              delta={metric.delta}
              status={metric.status}
              variant={metric.variant}
            />
          </div>
        ))}

      </div>

      <div className="flex shrink-0 items-center justify-end gap-2">
        <button
          type="button"
          aria-label="设置"
          title="设置"
          className="flex h-12 w-12 items-center justify-center border-2 border-stroke-ink bg-panel shadow-hard-sm sm:h-14 sm:w-14"
          onClick={() => push("stats-dashboard")}
        >
          <PixelIcon name="settings" size={16} />
        </button>
      </div>
    </header>
  );
};
