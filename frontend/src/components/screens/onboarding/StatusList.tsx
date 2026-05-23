import clsx from "clsx";

import { PixelIcon, type IconName } from "@/components/pixel";

export type StatusTone = "info" | "warn" | "alert";

export interface StatusItem {
  icon: IconName;
  title: string;
  subtitle?: string;
  tone: StatusTone;
}

export interface StatusListProps {
  items: StatusItem[];
  className?: string;
}

const TONE_CLASS: Record<StatusTone, string> = {
  info: "text-pixel-blue",
  warn: "text-pixel-orange",
  alert: "text-alarm-red",
};

export function StatusList({ items, className }: StatusListProps) {
  return (
    <ul className={clsx("grid gap-2", className)}>
      {items.slice(0, 4).map((item) => (
        <li key={item.title}>
          <div
            className={clsx(
              "relative flex items-start gap-3 border-2 border-stroke-ink bg-panel px-3 py-2 shadow-hard-sm",
              item.tone === "alert" && "pl-4",
            )}
          >
            {item.tone === "alert" ? (
              <span aria-hidden="true" className="absolute inset-y-0 left-0 w-1 bg-alarm-red" />
            ) : null}

            <span
              className={clsx(
                "flex h-8 w-8 shrink-0 items-center justify-center border-2 border-stroke-ink bg-panel-dim",
                TONE_CLASS[item.tone],
              )}
            >
              <PixelIcon name={item.icon} size={24} />
            </span>

            <div className="min-w-0 flex-1">
              <div className="truncate text-px-sm leading-tight text-ink-1">{item.title}</div>
              {item.subtitle ? (
                <div className="mt-1 break-words text-px-sm leading-tight text-ink-2">{item.subtitle}</div>
              ) : null}
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
