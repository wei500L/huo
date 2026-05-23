import clsx from "clsx";
import { ArrowDown } from "pixelarticons/react/ArrowDown";

import { PixelCard, PixelIcon, type IconName } from "@/components/pixel";

export interface Props {
  metricKey: "CASH" | "MORALE" | "BOARD" | "FACE";
  label: string;
  iconName: IconName;
  before: number;
  after: number;
  statusText: string;
  statusColor: "green" | "yellow" | "orange" | "red";
}

const BAR_CLASS: Record<Props["statusColor"], string> = {
  green: "bg-pixel-green text-white",
  yellow: "bg-caution-yellow text-ink-1",
  orange: "bg-pixel-orange text-white",
  red: "bg-pixel-red text-white",
};

const CHIP_CLASS: Record<Props["statusColor"], string> = {
  green: "bg-[#E8F5EA] text-pixel-green",
  yellow: "bg-[#FFF6D8] text-ink-1",
  orange: "bg-[#FFF1E1] text-pixel-orange",
  red: "bg-[#FFF0F0] text-pixel-red",
};

const formatValue = (metricKey: Props["metricKey"], value: number): string => {
  const formatted = Math.trunc(value).toLocaleString("zh-CN");
  return metricKey === "CASH" ? `¥${formatted}` : formatted;
};

const formatDelta = (metricKey: Props["metricKey"], delta: number): string => {
  const sign = delta > 0 ? "+" : "";
  return `${sign}${formatValue(metricKey, delta)}`;
};

const deltaClass = (delta: number): string => {
  if (delta > 0) return "text-pixel-green";
  if (delta < 0) return "text-pixel-red";
  return "text-ink-2";
};

export const MetricDiffCard = ({
  metricKey,
  label,
  iconName,
  before,
  after,
  statusText,
  statusColor,
}: Props) => {
  const delta = after - before;

  return (
    <PixelCard className="h-full min-h-[200px]">
      <div className="flex h-full flex-col">
        <div
          className={clsx(
            "-mx-3 -mt-3 mb-3 flex h-8 items-center border-b-2 border-stroke-ink px-3 text-px-sm leading-none",
            BAR_CLASS[statusColor],
          )}
        >
          <span className="truncate">{label}</span>
        </div>

        <div className="flex flex-1 flex-col gap-3 px-3 py-3">
          <div className="flex items-start gap-3">
            <div className="flex h-14 w-14 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim">
              <PixelIcon name={iconName} size={48} ariaLabel={label} />
            </div>

            <div className="min-w-0 flex-1">
              <div className="text-[10px] leading-none text-ink-3 line-through">
                上季 {formatValue(metricKey, before)}
              </div>

              <div className="mt-2 flex items-center gap-2">
                <ArrowDown aria-hidden="true" className="h-5 w-5 shrink-0 text-ink-2" />
                <div className={clsx("font-retro text-px-xl leading-none", deltaClass(delta))}>
                  {formatValue(metricKey, after)}
                </div>
              </div>

              <div className={clsx("mt-2 text-px-sm leading-none", deltaClass(delta))}>
                {formatDelta(metricKey, delta)}
              </div>
            </div>
          </div>

          <div
            className={clsx(
              "mt-auto inline-flex w-fit items-center gap-1 border-2 border-stroke-ink px-2 py-1 text-px-sm leading-none",
              CHIP_CLASS[statusColor],
            )}
          >
            <span className="h-2 w-2 border border-stroke-ink bg-current" aria-hidden="true" />
            <span>{statusText || "-"}</span>
          </div>
        </div>
      </div>
    </PixelCard>
  );
};
