import { PixelMetricCard, type PixelMetricCardProps } from "@/components/pixel";
import type { CompanyDTO, HistoryEntryDTO, StatsDTO } from "@/protocol/types";

type MetricKey = PixelMetricCardProps["metricKey"];

type MetricGridStats = StatsDTO & Partial<Record<"SALES" | "MKT", number>>;

interface MetricGridProps {
  stats: MetricGridStats;
  history: HistoryEntryDTO[];
  company?: CompanyDTO | null;
}

interface MetricConfig {
  key: MetricKey;
  label: string;
  iconName: PixelMetricCardProps["iconName"];
  variant: PixelMetricCardProps["variant"];
  fallbackValue: number;
}

const METRICS: MetricConfig[] = [
  { key: "cash", label: "现金流", iconName: "money", variant: "blue", fallbackValue: 0 },
  { key: "morale", label: "士气", iconName: "morale", variant: "green", fallbackValue: 0 },
  { key: "board", label: "董事会信任", iconName: "board", variant: "orange", fallbackValue: 0 },
  { key: "SALES", label: "员工人数", iconName: "users", variant: "purple", fallbackValue: 0 },
  { key: "MKT", label: "市场热度", iconName: "trending-up", variant: "red", fallbackValue: 0 },
  { key: "face", label: "公司体面", iconName: "face", variant: "gold", fallbackValue: 0 },
];

const METRIC_STATUS: Record<MetricKey, (value: number, dimmed: boolean) => string> = {
  cash: (value) => (value < 30 ? "危险" : value < 55 ? "承压" : "健康"),
  morale: (value) => (value < 35 ? "低迷" : value < 60 ? "中立" : "稳定"),
  board: (value) => (value < 50 ? "耐心下降" : value < 70 ? "观望" : "信任良好"),
  SALES: (_value, dimmed) => (dimmed ? "v2 开放" : "团队在线"),
  MKT: (_value, dimmed) => (dimmed ? "v2 开放" : "热度追踪"),
  face: (value) => (value < 30 ? "危险" : value < 55 ? "普通" : "体面良好"),
};

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

const getHistoricalValue = (entry: HistoryEntryDTO, key: MetricKey): number | null => {
  if (key === "SALES" || key === "MKT") {
    return null;
  }

  return entry.statsAfter[key];
};

const buildSparkline = (history: HistoryEntryDTO[], key: MetricKey, current: number): number[] => {
  const historyValues = history
    .slice(-4)
    .map((entry) => getHistoricalValue(entry, key))
    .filter((value): value is number => value !== null);
  const points = [...historyValues, current];
  const seed = points[0] ?? current;

  while (points.length < 7) {
    const offset = points.length % 2 === 0 ? 4 : -3;
    points.unshift(Math.max(0, Math.min(100, seed + offset * (7 - points.length))));
  }

  return points.slice(-7);
};

const getMetricValue = (config: MetricConfig, stats: MetricGridStats, company?: CompanyDTO | null): number => {
  if (config.key === "SALES") {
    return stats.SALES ?? company?.employeeCount ?? config.fallbackValue;
  }

  if (config.key === "MKT") {
    return stats.MKT ?? 50;
  }

  return stats[config.key] ?? config.fallbackValue;
};

const getDelta = (history: HistoryEntryDTO[], key: MetricKey, current: number): PixelMetricCardProps["delta"] => {
  const previous = history
    .slice()
    .reverse()
    .map((entry) => getHistoricalValue(entry, key))
    .find((value): value is number => value !== null);

  if (previous === undefined) {
    return undefined;
  }

  return { value: current - previous };
};

export const MetricGrid = ({ stats, history, company }: MetricGridProps) => {
  const metricV2Enabled = isMetricV2Enabled();

  return (
    <section aria-label="六大核心数据" className="grid grid-cols-[repeat(auto-fit,minmax(220px,1fr))] gap-px-md">
      {METRICS.map((metric) => {
        const isV2Metric = metric.key === "SALES" || metric.key === "MKT";
        const dimmed = isV2Metric && !metricV2Enabled;
        const value = dimmed ? 0 : getMetricValue(metric, stats, company);

        return (
          <PixelMetricCard
            key={metric.key}
            metricKey={metric.key}
            label={metric.label}
            iconName={metric.iconName}
            value={value}
            statusText={METRIC_STATUS[metric.key](value, dimmed)}
            delta={dimmed ? undefined : getDelta(history, metric.key, value)}
            sparkline={buildSparkline(history, metric.key, value)}
            variant={metric.variant}
            size="hero"
            dimmed={dimmed}
          />
        );
      })}
    </section>
  );
};
