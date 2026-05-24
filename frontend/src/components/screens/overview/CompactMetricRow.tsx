import { useMemo } from "react";

import { PixelMetricCard, type PixelMetricCardProps } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import { selectCurrentStats, selectHistory } from "@/store/selectors";
import type { HistoryEntryDTO, StatsDTO } from "@/protocol/types";

type MetricKey = PixelMetricCardProps["metricKey"];

interface MetricMeta {
  key: MetricKey;
  label: string;
  iconName: PixelMetricCardProps["iconName"];
  variant: PixelMetricCardProps["variant"];
  dimmed?: boolean;
}

const METRICS: MetricMeta[] = [
  { key: "cash", label: "现金流", iconName: "money", variant: "blue" },
  { key: "morale", label: "士气", iconName: "morale", variant: "green" },
  { key: "board", label: "董事会信任", iconName: "board", variant: "orange" },
  { key: "face", label: "公司体面", iconName: "face", variant: "gold" },
  { key: "SALES", label: "员工人数", iconName: "users", variant: "purple", dimmed: true },
  { key: "MKT", label: "市场热度", iconName: "trending-up", variant: "red", dimmed: true },
];

const FALLBACK_SERIES: Record<MetricKey, number[]> = {
  cash: [68, 69, 71, 67, 66, 70, 72],
  morale: [52, 54, 55, 56, 58, 57, 59],
  board: [49, 48, 47, 46, 45, 44, 43],
  face: [41, 42, 43, 44, 45, 46, 47],
  SALES: [38, 39, 40, 40, 41, 42, 42],
  MKT: [35, 34, 35, 36, 37, 38, 39],
};

const getHistoryValues = (history: HistoryEntryDTO[], key: MetricKey): number[] => {
  const values = history.slice(-7).map((entry) => {
    if (key === "SALES" || key === "MKT") {
      return FALLBACK_SERIES[key][0];
    }

    return entry.statsAfter[key];
  });

  const source = FALLBACK_SERIES[key];
  while (values.length < 7) {
    values.unshift(source[values.length] ?? source[0]);
  }

  return values.slice(-7);
};

const getMetricValue = (stats: StatsDTO | null, key: MetricKey): number => {
  if (!stats) {
    return FALLBACK_SERIES[key][FALLBACK_SERIES[key].length - 1];
  }

  if (key === "SALES" || key === "MKT") {
    return FALLBACK_SERIES[key][FALLBACK_SERIES[key].length - 1];
  }

  return stats[key];
};

const getStatusText = (key: MetricKey, value: number, dimmed?: boolean): string => {
  if (dimmed) {
    return "v1 占位";
  }

  if (key === "cash") return value < 30 ? "危险" : value < 55 ? "承压" : "健康";
  if (key === "morale") return value < 35 ? "低迷" : value < 60 ? "中立" : "稳定";
  if (key === "board") return value < 50 ? "耐心下降" : value < 70 ? "观望" : "信任良好";
  if (key === "face") return value < 30 ? "危险" : value < 55 ? "普通" : "体面良好";
  return "追踪中";
};

const getDelta = (history: HistoryEntryDTO[], key: MetricKey, current: number): PixelMetricCardProps["delta"] => {
  const previous = history
    .slice()
    .reverse()
    .map((entry) => (key === "SALES" || key === "MKT" ? null : entry.statsAfter[key]))
    .find((value): value is number => value !== null);

  return previous === undefined ? undefined : { value: current - previous };
};

export const CompactMetricRow = () => {
  const stats = useGameStore(selectCurrentStats);
  const history = useGameStore(selectHistory);

  const metrics = useMemo(
    () =>
      METRICS.map((metric) => {
        const value = getMetricValue(stats, metric.key);
        return {
          ...metric,
          value,
          statusText: getStatusText(metric.key, value, metric.dimmed),
          sparkline: getHistoryValues(history, metric.key),
          delta: metric.dimmed ? undefined : getDelta(history, metric.key, value),
        };
      }),
    [history, stats],
  );

  return (
    <section aria-label="六大核心指标" className="grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))] gap-3">
      {metrics.map((metric) => (
        <PixelMetricCard
          key={metric.key}
          metricKey={metric.key}
          label={metric.label}
          iconName={metric.iconName}
          value={metric.value}
          statusText={metric.statusText}
          delta={metric.delta}
          sparkline={metric.sparkline}
          variant={metric.variant}
          size="compact"
          dimmed={metric.dimmed}
        />
      ))}
    </section>
  );
};

export default CompactMetricRow;
