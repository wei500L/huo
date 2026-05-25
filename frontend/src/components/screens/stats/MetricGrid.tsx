import { PixelMetricCard, type PixelMetricCardProps } from "@/components/pixel";
import type { CompanyDTO, HistoryEntryDTO, StatsDTO } from "@/protocol/types";

type CoreMetricKey = keyof StatsDTO;

interface MetricGridProps {
  stats: StatsDTO;
  history: HistoryEntryDTO[];
  company?: CompanyDTO | null;
}

interface MetricConfig {
  key: CoreMetricKey;
  label: string;
  iconName: PixelMetricCardProps["iconName"];
  variant: PixelMetricCardProps["variant"];
}

const METRICS: MetricConfig[] = [
  { key: "cash", label: "现金流", iconName: "money", variant: "blue" },
  { key: "morale", label: "士气", iconName: "morale", variant: "green" },
  { key: "board", label: "董事会信任", iconName: "board", variant: "orange" },
  { key: "face", label: "公司体面", iconName: "face", variant: "gold" },
];

const METRIC_STATUS: Record<CoreMetricKey, (value: number) => string> = {
  cash: (value) => (value < 30 ? "危险" : value < 55 ? "承压" : "健康"),
  morale: (value) => (value < 35 ? "低迷" : value < 60 ? "中立" : "稳定"),
  board: (value) => (value < 50 ? "耐心下降" : value < 70 ? "观望" : "信任良好"),
  face: (value) => (value < 30 ? "危险" : value < 55 ? "普通" : "体面良好"),
};

const buildSparkline = (history: HistoryEntryDTO[], key: CoreMetricKey, current: number): number[] => {
  const historyValues = history
    .slice(-6)
    .map((entry) => entry.statsAfter[key]);
  return [...historyValues, current];
};

const getDelta = (history: HistoryEntryDTO[], key: CoreMetricKey, current: number): PixelMetricCardProps["delta"] => {
  const previous = history
    .slice()
    .reverse()
    .map((entry) => entry.statsAfter[key])
    .find((value) => typeof value === "number");

  if (previous === undefined) {
    return undefined;
  }

  return { value: current - previous };
};

export const MetricGrid = ({ stats, history, company: _company }: MetricGridProps) => {
  return (
    <section aria-label="六大核心数据" className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-px-md">
      {METRICS.map((metric) => {
        const value = stats[metric.key];

        return (
          <PixelMetricCard
            key={metric.key}
            metricKey={metric.key}
            label={metric.label}
            iconName={metric.iconName}
            value={value}
            statusText={METRIC_STATUS[metric.key](value)}
            delta={getDelta(history, metric.key, value)}
            sparkline={buildSparkline(history, metric.key, value)}
            variant={metric.variant}
            size="hero"
          />
        );
      })}
    </section>
  );
};
