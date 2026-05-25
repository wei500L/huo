import { useMemo } from "react";

import { PixelMetricCard, type PixelMetricCardProps } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import { selectCurrentStats, selectHistory } from "@/store/selectors";
import type { HistoryEntryDTO, StatsDTO } from "@/protocol/types";

type MetricKey = PixelMetricCardProps["metricKey"];
type CoreMetricKey = keyof StatsDTO;

interface MetricMeta {
  key: CoreMetricKey;
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
];

const getHistoryValues = (history: HistoryEntryDTO[], stats: StatsDTO, key: CoreMetricKey): number[] =>
  [...history.slice(-6).map((entry) => entry.statsAfter[key]), stats[key]];

const getStatusText = (key: CoreMetricKey, value: number): string => {
  if (key === "cash") return value < 30 ? "危险" : value < 55 ? "承压" : "健康";
  if (key === "morale") return value < 35 ? "低迷" : value < 60 ? "中立" : "稳定";
  if (key === "board") return value < 50 ? "耐心下降" : value < 70 ? "观望" : "信任良好";
  if (key === "face") return value < 30 ? "危险" : value < 55 ? "普通" : "体面良好";
  return "追踪中";
};

const getDelta = (history: HistoryEntryDTO[], key: CoreMetricKey, current: number): PixelMetricCardProps["delta"] => {
  const previous = history
    .slice()
    .reverse()
    .map((entry) => entry.statsAfter[key])
    .find((value) => typeof value === "number");

  return previous === undefined ? undefined : { value: current - previous };
};

export const CompactMetricRow = () => {
  const stats = useGameStore(selectCurrentStats);
  const history = useGameStore(selectHistory);

  const metrics = useMemo(
    () => {
      if (!stats) {
        return [];
      }

      return METRICS.map((metric) => {
        const value = stats[metric.key];
        return {
          ...metric,
          value,
          statusText: getStatusText(metric.key, value),
          sparkline: getHistoryValues(history, stats, metric.key),
          delta: getDelta(history, metric.key, value),
        };
      });
    },
    [history, stats],
  );

  if (!stats) {
    return (
      <section className="border-2 border-stroke-ink bg-panel px-px-md py-px-lg text-center text-px-md text-ink-2">
        等待后端指标快照
      </section>
    );
  }

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
