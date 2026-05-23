import clsx from "clsx";

import { PixelCard, PixelIcon } from "@/components/pixel";

export interface PromiseResultItem {
  quarter: string;
  status: "fulfilled" | "in_progress" | "failed";
  text: string;
  expected: string;
  result: string;
  delta?: string;
}

interface Props {
  items: PromiseResultItem[];
}

const STATUS_STYLE: Record<
  PromiseResultItem["status"],
  { tone: string; label: string; icon: "check" | "loader" | "close-box" }
> = {
  fulfilled: { tone: "text-pixel-green", label: "已兑现", icon: "check" },
  in_progress: { tone: "text-pixel-orange", label: "进行中", icon: "loader" },
  failed: { tone: "text-pixel-red", label: "已翻车", icon: "close-box" },
};

export const PromiseResultList = ({ items }: Props) => {
  const visibleItems = items.slice(0, 4);

  return (
    <PixelCard className="h-full" title="本季承诺结果" titleColor="ghost">
      <div className="space-y-0">
        <div className="grid grid-cols-[40px_56px_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_70px] gap-2 border-b-2 border-stroke-ink pb-2 text-[10px] leading-none text-ink-3">
          <span>Q</span>
          <span>状态</span>
          <span>标题</span>
          <span>预期</span>
          <span>结果</span>
          <span className="text-right">delta</span>
        </div>

        {visibleItems.map((item) => {
          const status = STATUS_STYLE[item.status];
          return (
            <div
              key={`${item.quarter}-${item.text}`}
              className="grid grid-cols-[40px_56px_minmax(0,1fr)_minmax(0,1fr)_minmax(0,1fr)_70px] items-center gap-2 border-b-2 border-panel-dim py-2 last:border-b-0"
            >
              <span className="flex h-8 items-center justify-center border-2 border-stroke-ink bg-panel-dim font-retro text-[9px] leading-none">
                {item.quarter}
              </span>

              <span className={clsx("flex items-center gap-1 text-px-sm leading-none", status.tone)}>
                <PixelIcon
                  ariaLabel={status.label}
                  className={clsx(item.status === "in_progress" && "animate-spin")}
                  name={status.icon}
                  size={16}
                />
                {status.label}
              </span>

              <span className="min-w-0 truncate text-px-sm leading-none text-ink-1">{item.text || "-"}</span>
              <span className="min-w-0 truncate text-px-sm leading-none text-ink-2">{item.expected || "-"}</span>
              <span className="min-w-0 truncate text-px-sm leading-none text-ink-1">{item.result || "-"}</span>
              <span className={clsx("text-right font-retro text-[9px] leading-none", status.tone)}>
                {item.delta || "—"}
              </span>
            </div>
          );
        })}
      </div>
    </PixelCard>
  );
};

