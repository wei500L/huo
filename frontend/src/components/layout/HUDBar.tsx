import { useEffect, useState } from "react";

import { PixelIcon } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import {
  selectCurrentCompany,
  selectCurrentQuarter,
  selectCurrentSnapshot,
  selectCurrentStats,
  selectHistory,
} from "@/store/selectors";
import { useScreenStore } from "@/store/screenStore";

import { DateCard, HUDMetric, LogoBadge } from "./hudParts";

const MAX_EMPLOYEES = 20;
const MOCK_TIME = "09:15";
const MOCK_DATE = "2025/05/26";
const MOCK_WEEKDAY = "周一";

const useViewportWidth = () => {
  const [width, setWidth] = useState(() => (typeof window === "undefined" ? 1280 : window.innerWidth));

  useEffect(() => {
    const updateWidth = () => {
      setWidth(window.innerWidth);
    };

    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  return width;
};

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

const formatMetricValue = (key: "CASH" | "MORALE" | "BOARD" | "FACE", value?: number): string => {
  if (!Number.isFinite(value ?? NaN)) {
    return "-/-";
  }

  const formatted = Math.trunc(value as number).toLocaleString("en-US");
  return key === "CASH" ? `¥${formatted}` : formatted;
};

const formatStatStatus = (key: "CASH" | "MORALE" | "BOARD" | "FACE", value?: number): string | undefined => {
  if (!Number.isFinite(value ?? NaN)) {
    return undefined;
  }

  const resolved = value as number;
  switch (key) {
    case "CASH":
      return resolved <= 5 ? "中立" : resolved >= 60 ? "健康" : "稳定";
    case "MORALE":
      return resolved >= 60 ? "健康" : resolved >= 35 ? "稳定" : "中立";
    case "BOARD":
      return resolved >= 55 ? "健康" : resolved >= 35 ? "稳定" : "中立";
    case "FACE":
      return resolved >= 45 ? "健康" : resolved >= 25 ? "稳定" : "中立";
    default:
      return undefined;
  }
};

export const HUDBar = () => {
  const viewportWidth = useViewportWidth();
  const snapshot = useGameStore(selectCurrentSnapshot);
  const stats = useGameStore(selectCurrentStats);
  const quarter = useGameStore(selectCurrentQuarter);
  const company = useGameStore(selectCurrentCompany);
  const history = useGameStore(selectHistory);
  const push = useScreenStore((state) => state.push);

  const showLegacyMetrics = viewportWidth >= 1280;
  const showStatus = viewportWidth >= 1024;
  const latestHistory = history[history.length - 1] ?? null;
  const employeeCount = typeof company?.employeeCount === "number" ? company.employeeCount : null;
  const previousStats = latestHistory?.statsBefore ?? null;

  const quarterNumber = quarter?.number ?? 0;
  const hasSnapshot = snapshot !== null;

  const coreMetrics = [
    {
      icon: "money" as const,
      label: "现金流",
      value: formatMetricValue("CASH", stats?.CASH),
      delta: formatDelta(stats?.CASH, previousStats?.CASH),
      status: showStatus ? formatStatStatus("CASH", stats?.CASH) : undefined,
      variant: "gold" as const,
    },
    {
      icon: "morale" as const,
      label: "士气",
      value: formatMetricValue("MORALE", stats?.MORALE),
      delta: formatDelta(stats?.MORALE, previousStats?.MORALE),
      status: showStatus ? formatStatStatus("MORALE", stats?.MORALE) : undefined,
      variant: "green" as const,
    },
    {
      icon: "board" as const,
      label: "董事会",
      value: formatMetricValue("BOARD", stats?.BOARD),
      delta: formatDelta(stats?.BOARD, previousStats?.BOARD),
      status: showStatus ? formatStatStatus("BOARD", stats?.BOARD) : undefined,
      variant: "blue" as const,
    },
    {
      icon: "face" as const,
      label: "面子",
      value: formatMetricValue("FACE", stats?.FACE),
      delta: formatDelta(stats?.FACE, previousStats?.FACE),
      status: showStatus ? formatStatStatus("FACE", stats?.FACE) : undefined,
      variant: "purple" as const,
    },
  ];

  const legacyMetrics = showLegacyMetrics
    ? [
        {
          icon: "trending-up" as const,
          label: "SALES",
          value: "v2",
          variant: "orange" as const,
          dimmed: true,
        },
        {
          icon: "trending-up" as const,
          label: "MKT",
          value: "v2",
          variant: "red" as const,
          dimmed: true,
        },
      ]
    : [];

  return (
    <header className="flex h-16 items-center gap-2 overflow-x-hidden overflow-y-visible border-b-2 border-stroke-ink bg-panel px-2">
      <LogoBadge />

      <DateCard
        day={quarterNumber}
        time={hasSnapshot ? MOCK_TIME : "-/-"}
        weekday={hasSnapshot ? MOCK_WEEKDAY : "--"}
        date={hasSnapshot ? MOCK_DATE : "--/--/--"}
      />

      <div className="flex min-w-0 flex-1 items-center gap-1 overflow-hidden">
        {coreMetrics.map((metric) => (
          <HUDMetric
            key={metric.label}
            icon={metric.icon}
            label={metric.label}
            value={metric.value}
            delta={metric.delta}
            status={metric.status}
            variant={metric.variant}
          />
        ))}

        {legacyMetrics.map((metric) => (
          <HUDMetric
            key={metric.label}
            icon={metric.icon}
            label={metric.label}
            value={metric.value}
            variant={metric.variant}
            dimmed={metric.dimmed}
          />
        ))}
      </div>

      <div className="flex shrink-0 items-center gap-2">
        {employeeCount !== null ? (
          <div className="flex h-12 items-center gap-1 border-2 border-stroke-ink bg-panel-dim px-2 shadow-hard-sm">
            <PixelIcon name="users" size={16} />
            <span className="whitespace-nowrap text-px-sm leading-none text-ink-1">
              {employeeCount}/{MAX_EMPLOYEES}
            </span>
          </div>
        ) : null}

        <button
          type="button"
          aria-label="Open stats dashboard"
          title="设置"
          className="flex h-12 w-12 items-center justify-center border-2 border-stroke-ink bg-panel shadow-hard-sm"
          onClick={() => push("stats-dashboard")}
        >
          <PixelIcon name="settings" size={16} />
        </button>
      </div>
    </header>
  );
};
