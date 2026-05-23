import clsx from "clsx";

import { PixelIcon, type IconName } from "@/components/pixel";

export interface MilestoneItem {
  value: number | string;
  label: string;
  achieved: boolean;
}

interface MilestoneListProps {
  items: MilestoneItem[];
  className?: string;
}

const formatValue = (value: MilestoneItem["value"]): string => {
  if (typeof value === "number") {
    return value.toLocaleString("zh-CN");
  }

  return value;
};

const resolveMilestoneIcon = (item: MilestoneItem): IconName => {
  if (item.label.includes("持股")) {
    return "coins";
  }

  if (item.label.includes("最大股东") || String(item.value).includes("终极")) {
    return "trophy";
  }

  return "star";
};

export const MilestoneList = ({ items, className }: MilestoneListProps) => {
  const visibleItems = items.slice(0, 10);

  return (
    <ul
      aria-label="复仇里程碑"
      className={clsx("max-h-[304px] space-y-px-sm overflow-y-auto pr-px-xs", className)}
    >
      {visibleItems.map((item, index) => {
        const iconName = resolveMilestoneIcon(item);
        const rowClassName = clsx(
          "flex w-full items-center gap-px-sm border-2 border-stroke-ink px-px-sm py-px-sm text-left shadow-hard-sm",
          item.achieved
            ? "bg-pixel-green/10 text-ink-1 hover:-translate-y-0.5"
            : "bg-panel-dim text-ink-3",
          item.achieved && "cursor-pointer transition-transform duration-75 ease-out",
        );
        const content = (
          <>
            <span
              aria-hidden="true"
              className={clsx(
                "flex h-8 w-8 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel",
                item.achieved ? "text-pixel-green" : "text-ink-3",
              )}
            >
              <PixelIcon name={iconName} size={16} />
            </span>
            <span className="min-w-0 flex-1">
              <span className="block truncate font-retro text-px-sm leading-tight text-ink-1">
                {formatValue(item.value)}
              </span>
              <span className="block truncate text-px-sm leading-tight">{item.label}</span>
            </span>
            <span
              className={clsx(
                "flex h-7 w-7 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel",
                item.achieved ? "text-pixel-green" : "text-ink-3",
              )}
            >
              <PixelIcon name={item.achieved ? "check" : "lock"} size={16} />
              <span className="sr-only">{item.achieved ? "已完成" : "未完成"}</span>
            </span>
          </>
        );

        if (item.achieved) {
          return (
            <li key={`${String(item.value)}-${item.label}-${index}`}>
              <button
                aria-label={`查看里程碑：${formatValue(item.value)} ${item.label}`}
                className={rowClassName}
                type="button"
                onClick={() => console.log(`[TODO] milestone detail: ${formatValue(item.value)} ${item.label}`)}
              >
                {content}
              </button>
            </li>
          );
        }

        return (
          <li key={`${String(item.value)}-${item.label}-${index}`}>
            <div className={rowClassName}>{content}</div>
          </li>
        );
      })}
    </ul>
  );
};
