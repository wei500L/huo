import clsx from "clsx";

import { PixelIcon, type IconName } from "@/components/pixel";

export interface SuggestedActionItem {
  color: "green" | "blue" | "red";
  title: string;
  subtitle: string;
  onClick: () => void;
}

interface Props {
  items: SuggestedActionItem[];
}

const COLOR_CLASS: Record<SuggestedActionItem["color"], { surface: string; hover: string }> = {
  green: { surface: "bg-pixel-green text-white", hover: "hover:bg-pixel-green/90" },
  blue: { surface: "bg-pixel-blue text-white", hover: "hover:bg-pixel-blue/90" },
  red: { surface: "bg-pixel-red text-white", hover: "hover:bg-pixel-red/90" },
};

const ACTION_ICON: Record<SuggestedActionItem["color"], IconName> = {
  green: "money",
  blue: "board",
  red: "trending-up",
};

export const SuggestedActions = ({ items }: Props) => {
  const visibleItems = items.slice(0, 3);

  return (
    <div className="flex h-full min-h-0 flex-col gap-2">
      {visibleItems.map((item) => {
        const style = COLOR_CLASS[item.color];
        return (
          <button
            key={item.title}
            type="button"
            onClick={item.onClick}
            className={clsx(
              "flex h-[58px] w-full items-center justify-between gap-2 border-2 border-stroke-ink px-3 text-left font-pixel text-px-sm leading-none shadow-hard transition-transform duration-75 ease-out",
              style.surface,
              style.hover,
              "hover:-translate-y-0.5 active:translate-y-0.5 active:shadow-none",
            )}
          >
            <span className="min-w-0 flex-1">
              <span className="block truncate text-px-base leading-none">{item.title}</span>
              <span className="mt-1 block truncate text-px-xs leading-none opacity-90">{item.subtitle}</span>
            </span>
            <span className="flex h-7 w-7 shrink-0 items-center justify-center border border-stroke-ink bg-panel-dim text-ink-1">
              <PixelIcon name={ACTION_ICON[item.color]} size={16} ariaLabel={item.title} />
            </span>
          </button>
        );
      })}
    </div>
  );
};

export default SuggestedActions;
