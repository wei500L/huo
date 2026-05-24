import { useMemo, useRef } from "react";

import { PixelButton, PixelCard, PixelIcon, PixelLineChart, type PixelLineChartSeries, type IconName } from "@/components/pixel";
import { useGameStore } from "@/store/gameStore";
import { selectHistory } from "@/store/selectors";
import { useElementSize } from "@/hooks/useElementSize";
import type { HistoryEntryDTO, StatsDTO } from "@/protocol/types";

type TrendKey = keyof StatsDTO | "SALES" | "MKT";

interface TrendMetric {
  key: TrendKey;
  label: string;
  iconName: IconName;
  color: string;
  dimmed?: boolean;
}

interface Props {
  onViewReport: () => void;
}

const TRENDS: TrendMetric[] = [
  { key: "cash", label: "现金流", iconName: "money", color: "#2E6FE6" },
  { key: "morale", label: "士气", iconName: "morale", color: "#3DAE5C" },
  { key: "board", label: "董事会信任", iconName: "board", color: "#F39A2B" },
  { key: "face", label: "公司体面", iconName: "face", color: "#7B5BE6" },
  { key: "SALES", label: "员工人数", iconName: "users", color: "#B5BAC3", dimmed: true },
  { key: "MKT", label: "市场热度", iconName: "trending-up", color: "#C7CBD3", dimmed: true },
];

const FALLBACK_MOCK: Record<TrendKey, number[]> = {
  cash: [68, 69, 71, 67, 66, 70, 72],
  morale: [52, 54, 55, 56, 58, 57, 59],
  board: [49, 48, 47, 46, 45, 44, 43],
  face: [41, 42, 43, 44, 45, 46, 47],
  SALES: [38, 39, 40, 40, 41, 42, 42],
  MKT: [35, 34, 35, 36, 37, 38, 39],
};

const getSeriesValues = (history: HistoryEntryDTO[], metric: TrendKey): number[] => {
  const entries = history.slice(-7);
  if (entries.length === 0) {
    return FALLBACK_MOCK[metric];
  }

  const values = entries.map((entry, index) => {
    if (metric === "SALES" || metric === "MKT") {
      return FALLBACK_MOCK[metric][index] ?? FALLBACK_MOCK[metric][FALLBACK_MOCK[metric].length - 1];
    }

    return entry.statsAfter[metric];
  });

  while (values.length < 7) {
    values.unshift(FALLBACK_MOCK[metric][values.length] ?? FALLBACK_MOCK[metric][0]);
  }

  return values.slice(-7);
};

const buildSeries = (history: HistoryEntryDTO[]): PixelLineChartSeries[] =>
  TRENDS.map((metric) => ({
    id: metric.key,
    label: metric.label,
    color: metric.color,
    values: getSeriesValues(history, metric.key),
  }));

export const TrendChartPanel = ({ onViewReport }: Props) => {
  const history = useGameStore(selectHistory);
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const chartSize = useElementSize(chartContainerRef);

  const series = useMemo(() => buildSeries(history), [history]);
  const xLabels = useMemo(() => ["1", "2", "3", "4", "5", "6", "7"], []);
  const chartWidth = Math.max(320, chartSize.width > 0 ? chartSize.width - 8 : 520);
  const chartHeight = Math.max(220, Math.round(chartWidth * 0.42));

  return (
    <PixelCard
      kind="info"
      title="本周趋势"
      badge={
        <PixelButton size="sm" variant="ghost" icon={<PixelIcon name="line-chart" size={16} ariaLabel="查看详细报告" />} onClick={onViewReport}>
          查看详细报告
        </PixelButton>
      }
      className="h-full min-h-[380px]"
    >
      <div className="grid h-full min-h-0 grid-cols-1 gap-3 xl:grid-cols-[minmax(220px,280px)_minmax(0,1fr)]">
        <div className="grid min-w-0 grid-cols-2 gap-2 pt-1 xl:flex xl:flex-col">
          {TRENDS.map((metric) => (
            <div
              key={metric.key}
              className="flex items-center gap-2 border-2 border-stroke-ink bg-panel px-3 py-2 text-px-sm leading-none"
              style={metric.dimmed ? { opacity: 0.58, filter: "grayscale(1)" } : undefined}
            >
              <span className="flex h-5 w-5 shrink-0 items-center justify-center border border-stroke-ink bg-panel-dim">
                <PixelIcon name={metric.iconName} size={16} ariaLabel={metric.label} />
              </span>
              <span className="min-w-0 truncate">{metric.label}</span>
            </div>
          ))}
        </div>

        <div ref={chartContainerRef} className="flex min-w-0 items-stretch justify-center xl:justify-end">
          <div className="flex w-full max-w-full flex-1 items-center border-2 border-stroke-ink bg-panel-dim p-1">
            <PixelLineChart width={chartWidth} height={chartHeight} series={series} xLabels={xLabels} showLegend={false} />
          </div>
        </div>
      </div>
    </PixelCard>
  );
};

export default TrendChartPanel;
